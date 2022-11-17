from django import forms
from .models import Companies
from .models import CompanyTypes
from .models import CompanySpheres


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CompaniesForm, self).__init__(*args, **kwargs)
        self.fields['company_type'] = forms.ModelChoiceField(queryset=CompanyTypes.objects.all(),
                                                             to_field_name='company_type',
                                                             empty_label='Select company type')
        self.fields['company_sphere'] = forms.ModelChoiceField(queryset=CompanySpheres.objects.all(),
                                                             to_field_name='company_sphere',
                                                             empty_label='Select company type')

# ['company_id', 'company_name', 'company_type', 'company_sphere', 'company_website']