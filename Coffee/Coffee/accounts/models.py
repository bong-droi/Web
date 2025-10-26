from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Chủ quán'),
        ('staff', 'Nhân viên'),
        ('customer', 'Khách hàng'),   # 👉 thêm role khách hàng
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"
