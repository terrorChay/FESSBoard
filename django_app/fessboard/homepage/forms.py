from django import forms
from .models import Companies

class CompaniesForm(forms.ModelForm):
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