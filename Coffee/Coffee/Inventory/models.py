from django.db import models

class Supply(models.Model):  # Vật tư / Nguyên liệu
    TYPE_CHOICES = (
        ("supply", "Vật tư"),
        ("ingredient", "Nguyên liệu"),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default="supply")
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)   # kg, lít, gói...
    quantity = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class Purchase(models.Model):  # Phiếu nhập vật tư
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
    quantity = models.FloatField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.supply.name} - {self.quantity} {self.supply.unit} - {self.date}"

class Damage(models.Model):  # Vật tư/Nguyên liệu hỏng
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
    quantity = models.FloatField()
    reason = models.CharField(max_length=255, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Hỏng: {self.supply.name} - {self.quantity} {self.supply.unit} - {self.date}"
