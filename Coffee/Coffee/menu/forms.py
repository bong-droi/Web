from django import forms
from .models import Category, MenuItem

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["name", "category", "price", "unit", "is_available", "image", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "in", "placeholder": "Tên món"}),
            "category": forms.Select(attrs={"class": "in"}),
            "price": forms.NumberInput(attrs={"class": "in", "min": 0, "step": 1000}),
            "unit": forms.TextInput(attrs={"class": "in", "placeholder": "ly / chai / bánh ..."}),
            "is_available": forms.CheckboxInput(attrs={"class": "chk"}),
            "description": forms.Textarea(attrs={"class": "in", "rows": 3, "placeholder": "Ghi chú / mô tả"}),
        }
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "is_active"]
        labels = {"name": "Tên danh mục", "is_active": "Đang dùng"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "in", "placeholder": "Ví dụ: Cà phê"}),
            "is_active": forms.CheckboxInput(attrs={"class": ""}),
        }