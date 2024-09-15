from django.contrib import admin
from django.contrib.auth.models import Group
from .models import CustomUser
from account.models import QuizAccess

admin.site.unregister(Group)

class CustomUserDisplay(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_verified', 'is_approved', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_verified', 'is_approved', ('date_joined', admin.DateFieldListFilter))


admin.site.register(CustomUser, CustomUserDisplay)


class QuizAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_pattern', 'access_granted_at', 'is_active')
    list_filter = ('question_pattern', 'is_active')
    search_fields = ('user__username', 'question_pattern__name')

admin.site.register(QuizAccess, QuizAccessAdmin)
