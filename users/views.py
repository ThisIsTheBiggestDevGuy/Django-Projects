from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.utils.encoding import force_bytes, force_str


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            #profile.objects.create(user=user)  # Create a Profile
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated successfully')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'users/profile.html', context)

#here is what should be reviewed:

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            #user = get_object_or_404(User, email=email) #this is makes it possible to have this done without login!
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_link = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # Send the password reset email
            subject = 'Reset your password'
            message = render_to_string('users/password_reset_email.html', {
                'reset_link': reset_link
            })
            send_mail(subject, message, 'sender@example.com', [email])
            
            messages.success(request, 'Password reset email sent. Please check your inbox.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    
    return render(request, 'users/password_reset.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Handle password reset confirmation logic
        # You can render a form to set a new password or perform any other necessary actions.
        return render(request, 'users/password_reset_confirm.html')
    else:
        # Handle invalid token or user not found
        return render(request, 'users/password_reset_invalid.html')
