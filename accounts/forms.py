from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        user = self.instance
        password_validation.validate_password(password1, user)
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from accounts.models import PasswordHistory
            PasswordHistory.objects.create(
                user=user,
                password=user.password
            )
            return user