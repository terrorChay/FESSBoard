from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView
from .models import Companies
from .forms import *


def index(request):
    form = CompaniesForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = CompaniesForm()
    return render(request, 'index.html', {'form': form})


def homepage(request):
    return render(request, 'homepage.html')


def Render_EventsForm(request):
    form = Events(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = EventsForm()
    return render(request, 'index.html', {'form': form})

def Render_UniForm(request):
    form = UniForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = UniForm()
    return render(request, 'index.html', {'form': form})


def Render_ProjectForm(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = ProjectForm()
    return render(request, 'index.html', {'form': form})

def Render_TeachersInProjectForm(request):
    form = TeachersInProjectForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = TeachersInProjectForm
    return render(request, 'index.html', {'form': form})


def MultipleRender(request):
    FormsDict = {
        'form_a': ProjectForm,
        'form_b': TeachersInProjectForm,
        'form_c': ProjectManagersForm,
        'form_d': ProjectManagersForm,
        'form_e': CuratorForm,
        'form_f': StudentsInGroupsForm,
    }
    forms = list(FormsDict.values())

    if request.method == 'POST':
        for i in forms:
            form = i(request.POST or None)
            if form.is_valid():
                form.save()
            messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        return render(request, 'AddProject.html', FormsDict)



def Render_ComplexProject(request):
    form_a = ProjectForm(request.POST or None)
    form_b = TeachersInProjectForm(request.POST or None)
    form_c = ProjectManagersForm(request.POST or None)
    form_d = ProjectManagersForm(request.POST or None)
    form_e = CuratorForm(request.POST or None)
    form_f = StudentsInGroupsForm(request.POST or None)
    return render(request, 'AddProject.html', {'form_a': form_a, 'form_b': form_b, 'form_c': form_c, 'form_d': form_d, 'form_e': form_e, 'form_f': form_f,})

