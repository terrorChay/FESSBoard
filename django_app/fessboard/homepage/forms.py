from django import forms
from .models import *
# from .models import Companies
# from .models import CompanyTypes
# from .models import CompanySpheres


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CompaniesForm, self).__init__(*args, **kwargs)
        self.fields['company_type'] = forms.ModelChoiceField(queryset=CompanyTypes.objects.all(),
                                                             # to_field_name='company_type',
                                                             empty_label='Select company type')
        self.fields['company_sphere'] = forms.ModelChoiceField(queryset=CompanySpheres.objects.all(),
                                                             to_field_name='company_sphere',
                                                             empty_label='Select company sphere')

# ['company_id', 'company_name', 'company_type', 'company_sphere', 'company_website']


class EventsForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = '__all__'


class UniForm(forms.ModelForm):
    class Meta:
        model = Universities
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UniForm, self).__init__(*args, **kwargs)
        self.fields['university_region'] = forms.MultipleChoiceField(queryset=Regions.objects.all(),
                                                             to_field_name='region',
                                                             empty_label='Its location')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = '__all__'
        widgets = {
            'is_frozen': forms.RadioSelect(choices=[('1', 'true'), ('0', 'false')])
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['project_grade'] = forms.ModelChoiceField(queryset=ProjectGrades.objects.all(),
                                                             to_field_name='grade',
                                                             empty_label='Select project grade')
        self.fields['project_field'] = forms.ModelChoiceField(queryset=ProjectFields.objects.all(),
                                                             to_field_name='field',
                                                             empty_label='Select project field')
        self.fields['project_company'] = forms.ModelChoiceField(queryset=Companies.objects.all(),
                                                              to_field_name='company_name',
                                                              empty_label='Select project company')


class TeachersInProjectForm(forms.ModelForm):
    class Meta:
        model = TeachersInProjects
        fields = 'teacher_id',

    def __init__(self, *args, **kwargs):
        super(TeachersInProjectForm, self).__init__(*args, **kwargs)
        self.fields['teacher_id'] = forms.ModelMultipleChoiceField(queryset=Teachers.objects.all(),
                                                                   to_field_name='teacher_surname'
                                                                   )



class ProjectManagersForm(forms.ModelForm):
    class Meta:
        model = ProjectManagers
        fields = 'student',

    def __init__(self, *args, **kwargs):
        super(ProjectManagersForm, self).__init__(*args, **kwargs)
        self.fields['student'] = forms.ModelMultipleChoiceField(queryset=Students.objects.all(),
                                                                to_field_name='student_surname')


class CuratorForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = 'curator',

    def __init__(self, *args, **kwargs):
        super(CuratorForm, self).__init__(*args, **kwargs)
        self.fields['curator'] = forms.ModelChoiceField(queryset=Students.objects.all(),
                                                        to_field_name='student_surname',
                                                        empty_label='Select a curator')


class StudentsInGroupsForm(forms.ModelForm):
    class Meta:
        model = StudentsInGroups
        fields = 'student',

    def __init__(self, *args, **kwargs):
        super(StudentsInGroupsForm, self).__init__(*args, **kwargs)
        self.fields['student'] = forms.ModelMultipleChoiceField(queryset=Students.objects.all(),
                                                                to_field_name='student_surname')