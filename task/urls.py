from django.urls import path
from .views import TaskListCreate, TaskUpdateDetail

urlpatterns = [
    path("api/v1/tasks/", TaskListCreate.as_view(), name="tasks"),
    path("api/v1/task/<int:pk>/", TaskUpdateDetail.as_view(), name="task-update"),
]