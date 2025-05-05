from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str

tasks=[]

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return {"message":"Tâche ajoutée","task":task}

@app.get("/tasks")
def get_tasks():
    return tasks




