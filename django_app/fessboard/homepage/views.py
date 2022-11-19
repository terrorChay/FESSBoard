from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView
from .models import Companies
from .forms import *


def company_view(request):
    form = CompaniesForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = CompaniesForm()
    return render(request, 'index.html', {'form': form})


def student_view(request):
    form = StudentsForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = StudentsForm()
    return render(request, 'index.html', {'form': form})


def homepage(request):
    return render(request, 'homepage.html')


