from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from decimal import Decimal


User = get_user_model()

# Create your models here.
class Notification(models.Model):
    message = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class PointSetting(models.Model):
    per_point = models.FloatField(default=0.0)
    currency = models.CharField(max_length=100, default='USDT')
    min_withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Reject', 'Reject'),
        ('Complete', 'Complete')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_address = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.user.username} at {self.timestamp}"

@receiver(post_save, sender=Withdrawal)
def update_user_balance(sender, instance, **kwargs):
    if instance.status == 'Reject':
        user = instance.user
        point_setting = PointSetting.objects.first()
        per_point = point_setting.per_point
        user.point = Decimal(user.point) + Decimal(instance.amount) / Decimal(per_point)
        if user.point < 0:
            raise ValidationError("User's balance cannot be negative")
        user.save()