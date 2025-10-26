from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        db_table = "menu_category"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    name = models.CharField("Tên món", max_length=150)
    price = models.DecimalField("Giá bán", max_digits=12, decimal_places=0)
    unit = models.CharField("Đơn vị", max_length=20, default="ly", blank=True)
    is_available = models.BooleanField("Đang bán", default=True)
    image = models.ImageField("Ảnh", upload_to="menu/", blank=True, null=True)
    description = models.TextField("Mô tả", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Món"
        verbose_name_plural = "Món"

    def __str__(self):
        return self.name
