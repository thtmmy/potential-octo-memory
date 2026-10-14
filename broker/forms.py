from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,  SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import *
from django.forms import ModelForm


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,  SetPasswordForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from .models import *
from django.forms import ModelForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='A valid email address, please.', required=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class DepositForm (ModelForm):
    class Meta:
        model = Deposit
        fields = '__all__'
        exclude = ['user']

class ProfileSettingsForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = ProfileSettings
        fields = [
            "phone_number",
            "date_of_birth",
            "nationality",
            "bank_name",
            "account_name",
            "account_number",
            "swift_code",
            "bitcoin_address",
            "ethereum_address",
            "litecoin_address",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.instance.user if self.instance and self.instance.pk else None

        if user:
            self.fields["full_name"].initial = (
                f"{user.first_name} {user.last_name}".strip()
            )
            self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        user = self.instance.user

        if User.objects.filter(email__iexact=email).exclude(
            pk=user.pk
        ).exists():
            raise forms.ValidationError(
                "This email address is already in use."
            )

        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        full_name = self.cleaned_data["full_name"].strip()
        name_parts = full_name.split()

        user.first_name = name_parts[0] if name_parts else ""
        user.last_name = " ".join(name_parts[1:])
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            profile.save()

        return profile


class SecurePasswordChangeForm(PasswordChangeForm):
    pass

class WalletForm (ModelForm):
    class Meta:
        model = Wallet
        fields = '__all__'
        exclude = ['user']

class PinForm (ModelForm):
    class Meta:
        model = Pin
        fields = '__all__'
        exclude = ['user', 'name']