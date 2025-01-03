from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import valkey
import threading


app = FastAPI(title="Task Management System", description="A simple API", version="1.0")


class ConfigManager:
    def __init__(self):
        self.config_client = valkey.Valkey(host="localhost", port=6379)

    def get_config(self, key):
        return self.config_client.get(key)

config_manager = ConfigManager()
DATABASE_URL = config_manager.get_config('database_uri') or 'mysql+pymysql://user:password@localhost/task_db'

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")


class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    user_id: int | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    user_id: int | None

    class Config:
        orm_mode = True


class PubSubManager:
    def __init__(self):
        self.client = valkey.Valkey(host="localhost", port=6379)
        self.pubsub = self.client.pubsub()
        self.subscribed_channels = []

    def publish(self, channel, message):
        self.client.publish(channel, message)

    def subscribe(self, channel, callback):
        if channel not in self.subscribed_channels:
            self.pubsub.subscribe(channel)
            self.subscribed_channels.append(channel)

        def listen():
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    callback(message["data"])

        threading.Thread(target=listen, daemon=True).start()

pubsub_manager = PubSubManager()

def log_message(data):
    print(f"[LOG] Received message: {data}")

pubsub_manager.subscribe("logs", log_message)


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Publish message
    pubsub_manager.publish("logs", f"New user created: {user.username}")
    return db_user

@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.title, description=task.description, user_id=task.user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Publish message
    pubsub_manager.publish("logs", f"New task created: {task.title}")
    return db_task

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database initialized")
