from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView
from .models import Companies
from .forms import CompaniesForm


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


