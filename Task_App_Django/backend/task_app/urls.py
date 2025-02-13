from . import views
from django.urls import path

app_name = "tasks"
urlpatterns = [
    path("", view=views.index, name="tasks"),   
    path("<int:task_id>/", view=views.task_detail, name="detail")
]

