import pandas as pd
from django import forms
from .models import *

from datetime import datetime


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CompaniesForm, self).__init__(*args, **kwargs)
        self.fields['company_type'] = forms.ModelChoiceField(queryset=CompanyTypes.objects.all(),
                                                             to_field_name='company_type',
                                                             empty_label='Выберите тип компании',
                                                             widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['company_sphere'] = forms.ModelChoiceField(queryset=CompanySpheres.objects.all(),
                                                             to_field_name='company_sphere',
                                                             empty_label='Выберите сферу компании',
                                                            widget=forms.Select(attrs={'class': 'form-control'}))


class StudentsForm(forms.ModelForm):

    class Meta:
        def possible_years(first_year_in_scroll, last_year_in_scroll):
            p_year = []
            for i in range(first_year_in_scroll, last_year_in_scroll, -1):
                p_year_tuple = str(i), i
                p_year.append(p_year_tuple)
            return p_year + [('', '----')]
        model = Students
        fields = '__all__'
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_surname': forms.TextInput(attrs={'class': 'form-control'}),
            'student_midname': forms.TextInput(attrs={'class': 'form-control'}),
            'bachelor_start_year': forms.Select(attrs={'class': 'form-control'}, choices=possible_years(
                (datetime.now()).year, 2014)),
            'master_start_year': forms.Select(attrs={'class': 'form-control'}, choices=possible_years(
                (datetime.now()).year, 2014)),
        }

    def __init__(self, *args, **kwargs):
        super(StudentsForm, self).__init__(*args, **kwargs)
        self.fields['bachelors_university'] = forms.ModelChoiceField(queryset=Universities.objects.all(),
                                                             to_field_name='university_name',
                                                             empty_label='Выберите университет бакалавра',
                                                             widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['masters_university'] = forms.ModelChoiceField(queryset=Universities.objects.all(),
                                                             to_field_name='university_name',
                                                             empty_label='Выберите университет магистратуры',
                                                            widget=forms.Select(attrs={'class': 'form-control'}), required=False)
        self.fields['student_status'] = forms.ModelChoiceField(queryset=StudentStatuses.objects.all(),
                                                                   to_field_name='student_status',
                                                                   empty_label='Выберите статус студента',
                                                                   widget=forms.Select(attrs={'class': 'form-control'}))

