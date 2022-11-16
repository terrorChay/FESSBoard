from django import forms
from .models import Companies


class CompaniesForm(forms.ModelForm):
    #company_type = Companies.objects.distinct('company_type')
    #company_sphere = Companies.objects.distinct('company_sphere')
    #type_args = [company_type, company_sphere]

    class Meta:
        model = Companies
        fields = '__all__'
        exclude = ['company_id']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'company_sphere': forms.Select(attrs={'class': 'form-control'}),
            'company_website': forms.TextInput(attrs={'class': 'form-control'})
        }

# ['company_id', 'company_name', 'company_type', 'company_sphere', 'company_website']