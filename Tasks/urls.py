from django.urls import path
from . import views
from .views import TaskListCreateAPIView,  TaskRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('create/', views.task_create, name='task_create'),
    path('<int:pk>/update/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('api/tasks/', TaskListCreateAPIView.as_view(), name='task-api-list'),
    path('api/tasks/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='task_detail_update_delete')

]