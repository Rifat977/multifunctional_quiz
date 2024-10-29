from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from .models import CustomUser
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string, constant_time_compare

from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

from course.models import Course


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']  # Get the identifier from the form
            password = form.cleaned_data['password']
            
            if '@' in identifier:
                user = CustomUser.objects.get(email=identifier)
                identifier = user.username
            
            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                if user.is_verified:
                    if user.is_approved:
                        if user.is_active:
                            login(request, user)
                            return redirect('core:home')
                        else:
                            messages.error(request, 'Your account is inactive. Please contact the administrator.')
                    else:
                        messages.error(request, 'Your account is unapproved. Please contact the administrator.')
                else:
                    messages.error(request, 'Your account is unverified. Please verify your account.')
            else:
                messages.error(request, 'Invalid username, email, or password.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = LoginForm()
    
    return render(request, 'user/auth/login.html', {'form': form})

#registration process

def register(request):
    courses = Course.objects.filter(status=True)
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = default_token_generator.make_token(user)
            user.email_verification_token = token
            user.email_verification_sent_at = timezone.now()
            user.save()

            send_verification_email(user)
            return redirect('account:verification_sent')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'user/auth/register.html', {'form': form, 'courses':courses})

def send_verification_email(user):

    subject = 'Verify your email address'
    token = user.email_verification_token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = f"http://dev.entrancequiz.com/account/verify-email/{uid}/{token}/"
    message = f'Click the following link to verify your email address: {verification_url}'
    send_mail(subject, message, 'Entrance Quiz <support@entrancequiz.com>', [user.email])

def verification_sent(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'user/auth/verification_sent.html')

def verify_email(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('core:home')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if user.is_verified:
                messages.success(request, 'Email already verified.')
            else:
                user.is_verified = True
                user.is_active = True
                user.save()
                messages.success(request, 'Email verified successfully.')
            return redirect('account:verification_success')
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('account:verification_failed')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('account:verification_failed')

def verification_failed(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'user/auth/verification_failed.html')

def verification_success(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'user/auth/verification_success.html')

## end registraiton

def reset_password(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            
            if user is not None:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                reset_link = reset_url = request.build_absolute_uri(f"/account/new-password/{uid}/{token}/")
                send_mail(
                    'Password Reset',
                    f'Click the following link to reset your password: {reset_link}',
                    'Entrance Quiz <support@entrancequiz.com>',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'A password reset link has been sent to your email.')
                return redirect('account:confirm_password')
            else:
                messages.error(request, 'No user found with that email address.')
    else:
        form = PasswordResetForm()
    return render(request, 'user/auth/reset_password.html')

def confirm_password(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'user/auth/confirm_password.html')

def new_password(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('core:home')

    uid = force_str(urlsafe_base64_decode(uidb64))
    try:
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Your password has been successfully updated.')
                return redirect('account:login')
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, 'The password reset link is invalid.')
        return redirect('account:new_password')

    # If form validation fails, include form errors in the context
    return render(request, 'user/auth/new_password.html', {'uidb64': uidb64, 'token': token, 'form': form})

@login_required
def logout(request):
    if request.method=="POST":
        auth.logout(request)
        return redirect('core:index')


@login_required
def profile_setting(request):
    user = request.user
    courses = Course.objects.all()
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        gender = request.POST.get('gender')
        avatar = request.FILES.get('avatar')

        errors = {}

        #if not message:
         #   errors['message'] = 'Message name is required.'

        if not first_name:
            errors['first_name'] = 'First name is required.'

        if not last_name:
            errors['last_name'] = 'Last name is required.'

        if not gender:
            errors['gender'] = 'Gender is required.'

        if old_password and (not new_password or not confirm_password):
            errors['password'] = 'New password and confirm password are required when changing password.'
        elif old_password and new_password != confirm_password:
            errors['password'] = 'New password and confirm password do not match.'
        elif old_password and not request.user.check_password(old_password):
            errors['password'] = 'Old password is incorrect.'

        if avatar and not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            errors['avatar'] = 'Avatar must be an image file (JPG, JPEG, PNG, GIF).'

        if errors:
            for field, error_message in errors.items():
                messages.error(request, error_message)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.gender = gender
            if new_password:
                user.set_password(new_password)
            if avatar:
                user.avatar = avatar
            user.save()
            messages.success(request, 'Profile updated successfully.')

        return redirect('account:profile_settings')
    
    return render(request, 'user/profile_settings.html', {'user': user, 'courses': courses})
