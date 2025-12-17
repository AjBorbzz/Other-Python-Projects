from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

class Task(BaseModel):
    id : Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

task_db = []
task_id_counter=1

@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    global task_id_counter

    task.id = task_id_counter
    task_id_counter += 1

    task_db.append(task)
    return task