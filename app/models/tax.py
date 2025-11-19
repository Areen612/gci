from django.db import models

class Tax(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=4)  # e.g. 0.0825
    compounding = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.rate*100}%)"