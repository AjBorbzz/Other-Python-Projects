from django.shortcuts import render, HttpResponse
from .models import Tasks
from django.template import loader

def index(request):
    latest_tasks = Tasks.objects.all()
    context= {
        "latest_tasks": latest_tasks
    }
    return render(request, "task_app/index.html", context)

def task_detail(request, task_id):
    task = Tasks.objects.get(pk=task_id)
    return HttpResponse(f"Your detailed task: {task.id} - {task.description} - {task.pub_date}")

