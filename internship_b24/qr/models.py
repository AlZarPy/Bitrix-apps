import uuid
from django.db import models

class ProductLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product_id = models.PositiveIntegerField(db_index=True)

    title_cached = models.CharField(max_length=512, blank=True)
    img_url_cached = models.URLField(blank=True)
    price_cached = models.CharField(max_length=64, blank=True)
    currency_cached = models.CharField(max_length=16, blank=True)
    description_cached = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=128, blank=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_id} -> {self.id}"
