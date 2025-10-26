from django import forms
from .models import StaffProfile, Salary

class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['user', 'phone', 'address', 'hire_date']

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['user', 'month', 'amount']
