from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # path("", include("home.urls")),
    path("tasks/", include("task_app.urls")),
    path("admin/", admin.site.urls),
]
