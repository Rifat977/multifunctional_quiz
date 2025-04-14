from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from course.models import Course
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from time import timezone

from course.models import QuestionPattern

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    point = models.FloatField(default=0.0)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    def is_email_verification_token_expired(self):
        if self.email_verification_sent_at:
            expiration_time = timezone.timedelta(hours=24)  # 24 hours validity
            return self.email_verification_sent_at + expiration_time < timezone.now()
        return True

    def generate_password_reset_token(self):
        token = get_random_string(length=32)
        self.password_reset_token = token
        self.save()
        return token

class QuizAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question_pattern = models.ForeignKey(QuestionPattern, on_delete=models.CASCADE)
    access_granted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.question_pattern.name}"


@receiver(models.signals.pre_save, sender=CustomUser)
def notify_user_on_approval(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CustomUser.objects.get(pk=instance.pk)
        except CustomUser.DoesNotExist:
            return

        # if instance.is_approved and not old_instance.is_approved and instance.is_verified:
        #     send_mail(
        #         'Your profile has been approved',
        #         'Your profile has been approved. You can now access the site.',
        #         'Entrance Quiz <support@entrancequiz.com>',
        #         [instance.email],
        #         fail_silently=False,
        #     )
