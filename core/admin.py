from django.contrib import admin
from .models import Notification, PointSetting, Withdrawal

# Register your models here.
admin.site.register(Notification)
admin.site.register(PointSetting)

class WithdrawalDisplay(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'timestamp')
    search_fields = ('user', 'amount', 'payment_method', 'status', 'timestamp')
    list_filter = ('timestamp',)


admin.site.register(Withdrawal, WithdrawalDisplay)