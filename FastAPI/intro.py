from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

class Task(BaseModel):
    id : Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

task_db = []
task_id_counter=1

@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    global task_id_counter

    task.id = task_id_counter
    task_id_counter += 1

    task_db.append(task)
    return task

@app.get("/tasks")
def get_tasks():
    return task_db

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in task_db:
        if task.id == task_id:
            return task 
        
    raise HTTPException(status_code=404, detail="Task Not Found!")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    for task in task_db:
        if task.id == task_id:
            # Update only provided fields
            if task_update.title is not None:
                task.title = task_update.title
            if task_update.description is not None:
                task.description = task_update.description
            if task_update.completed is not None:
                task.completed = task_update.completed
            return task
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(task_db):
        if task.id == task_id:
            task_db.pop(index)
            return {"message": "Task deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Task not found")