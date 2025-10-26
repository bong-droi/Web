from django.db import models
from django.conf import settings
from menu.models import MenuItem

class Order(models.Model):
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    ORDER_TYPE_CHOICES = (
        ("online", "Online"),
        ("offline", "Offline"),
    )
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default="offline")
    delivery_address = models.CharField(max_length=255, blank=True, default="")
    table_number = models.CharField(max_length=20, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")

    STATUS_CHOICES = (
        ("processing", "Đang xử lý"),
        ("processed", "Đã xử lý"),
        ("canceled", "Đã hủy"),
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="processing")
    completed_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Order #{self.id} - {self.staff.username if self.staff else 'N/A'}"

    def total_price(self):
        return sum(item.menu_item.price * item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
