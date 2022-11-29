from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView
from .models import Companies
from .forms import *


def createCompany(request):
    form = CompaniesForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/company-hub/')
    else:
        form = CompaniesForm()
    return render(request, 'index.html', {'form': form})


def updateCompany(request, pk):
    company = Companies.objects.get(company_id=pk)
    form = CompaniesForm(instance=company)

    if request.method == 'POST':
        form = CompaniesForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/company-hub/')

    context = {'form': form, 'company': company}
    return render(request, 'index.html', context)


def deleteCompany(request, pk):
    company = Companies.objects.get(company_id=pk)
    context = {'item': company}
    if request.method == 'POST':
        company.delete()
        return HttpResponseRedirect('/company-hub/')
    return render(request, 'delete.html', context)


def companyHub(request):
    context = {'Companies': Companies.objects.all()}
    return render(request, 'company_hub.html', context)


def student_view(request):
    form = StudentsForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = StudentsForm()
    return render(request, 'index.html', {'form': form})


def project_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST':
        form.save()
        messages.success(request, "Form saved successfully!")
        return HttpResponseRedirect('/')
    else:
        form = ProjectForm()
    return render(request, 'index.html', {'form': form})


def homepage(request):
    return render(request, 'main.html')


