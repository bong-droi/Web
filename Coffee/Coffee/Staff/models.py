from django.db import models
from django.conf import settings

class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.phone}"

class Salary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.DateField()   # lưu ngày đầu tháng
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.month} : {self.amount}"
