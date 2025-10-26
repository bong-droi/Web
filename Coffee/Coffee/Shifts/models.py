from django.db import models
from django.conf import settings

class Shift(models.Model):
    name = models.CharField(max_length=50)              # Ví dụ: Ca sáng
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=0)   # Số NV tối đa trong ca (0 = không giới hạn)
    date = models.DateField(null=True, blank=True)      # Ngày áp dụng (tuỳ chọn)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class ShiftRegistration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'shift', 'date')     # 1 nhân viên không đăng ký 2 lần cho cùng ca

class AssignedShift(models.Model):
    """Chủ quán chỉ định nhân viên làm ca (bản chất giống đăng ký nhưng do owner tạo)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'shift', 'date')

class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    )
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swap_requests_sent')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swap_requests_received')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['responder', 'status']),
        ]
