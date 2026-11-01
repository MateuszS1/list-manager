from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from manager.models import Task, Tag


class TaskListView(generic.ListView):
    model = Task
    context_object_name = "task_list"


class TagListView(generic.ListView):
    model = Tag


class TaskCreateView(generic.CreateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("manager:task-list")


class TagCreateView(generic.CreateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("manager:tag-list")


class TaskUpdateView(generic.UpdateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("manager:task-list")


class TagUpdateView(generic.UpdateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("manager:tag-list")


class TaskDeleteView(generic.DeleteView):
    model = Task
    success_url = reverse_lazy("manager:task-list")


class TagDeleteView(generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("manager:tag-list")


def task_swap_status(request, pk):
    task = Task.objects.get(pk=pk)
    task.is_completed = not task.is_completed
    task.save()

    return HttpResponseRedirect(reverse_lazy("manager:task-list"))
