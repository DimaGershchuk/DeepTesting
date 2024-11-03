from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from .models import Task
from .forms import TaskForm
from .serializers import TaskSerializer


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'task_list.html', {'tasks': tasks})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'task_detail.html', {'task': task})


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form, 'task': task})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'task_confirm_delete.html', {'task': task})


class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer