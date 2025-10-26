from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
# accounts/forms.py
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
User = get_user_model()

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class":"input__control"}),
            "first_name": forms.TextInput(attrs={"class":"input__control"}),
            "last_name": forms.TextInput(attrs={"class":"input__control"}),
            "email": forms.EmailInput(attrs={"class":"input__control"}),
        }

class RoleForm(forms.ModelForm):
    """Chỉ cho phép: khách -> nhân viên; nhân viên không được xuống khách; không cho lên chủ.
    Chủ quán giữ nguyên (không đổi role bằng form này).
    """
    class Meta:
        model = User
        fields = ["role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        # Lọc lựa chọn theo role hiện tại
        if instance is not None:
            current = getattr(instance, "role", "customer")
            if current == "customer":
                self.fields["role"].choices = [("customer", "Khách hàng"), ("staff", "Nhân viên")]
            elif current == "staff":
                self.fields["role"].choices = [("staff", "Nhân viên")]
            elif current == "owner":
                # Không cho chỉnh: chỉ hiển thị hiện trạng
                self.fields["role"].choices = [("owner", "Chủ quán")]

    def clean_role(self):
        role = self.cleaned_data.get("role")
        instance = getattr(self, "instance", None)
        current = getattr(instance, "role", None)
        # Chặn tất cả đường đi ngoài quy tắc
        if current == "owner" and role != "owner":
            raise forms.ValidationError("Không thể thay đổi vai trò của chủ quán tại đây.")
        if current == "staff" and role != "staff":
            raise forms.ValidationError("Nhân viên không được chuyển xuống khách.")
        if current == "customer" and role not in ("customer", "staff"):
            raise forms.ValidationError("Chỉ cho phép khách chuyển lên nhân viên.")
        if role == "owner":
            # Bỏ chức năng lên chủ tại form này
            raise forms.ValidationError("Không hỗ trợ nâng lên chủ quán tại đây.")
        return role

class QuickCreateStaffForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email"]  # thêm các trường bạn muốn

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "customer"   # mặc định khách hàng
        if commit:
            user.save()
        return user
