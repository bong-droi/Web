from django import forms
from .models import Supply, Purchase, Damage

class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ['type', 'name', 'unit', 'quantity']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supply', 'quantity', 'cost']

class DamageForm(forms.ModelForm):
    class Meta:
        model = Damage
        fields = ['supply', 'quantity', 'reason']
