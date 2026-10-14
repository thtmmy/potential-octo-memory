from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from .forms import UserRegistrationForm, UserLoginForm, SetPasswordForm, PasswordChangeForm
from .decorators import user_not_authenticated
from .tokens import account_activation_token
from .models import *
from .forms import *
from django.http import HttpResponse
# Create your views here.
from decimal import Decimal, InvalidOperation




def index(request):
    context = {}
    return render (request, "broker/index.html", context)

@user_not_authenticated
def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            login_input = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"]

            # Accept either username or email address.
            user_record = None

            if "@" in login_input:
                matching_users = User.objects.filter(
                    email__iexact=login_input
                )

                if matching_users.count() == 1:
                    user_record = matching_users.first()
                elif matching_users.count() > 1:
                    messages.error(
                        request,
                        "Multiple accounts use this email. Please contact support."
                    )
                else:
                    messages.error(request, "Invalid username/email or password.")

            else:
                user_record = User.objects.filter(
                    username__iexact=login_input
                ).first()

                if user_record is None:
                    messages.error(request, "Invalid username/email or password.")

            if user_record is not None:
                user = authenticate(
                    request,
                    username=user_record.get_username(),
                    password=password,
                )

                if user is not None:
                    login(request, user)
                    messages.success(
                        request,
                        f"Welcome, {user.username}! You have been logged in."
                    )
                    return redirect("dashboard")

                messages.error(request, "Invalid username/email or password.")

        else:
            for key, errors in form.errors.items():
                if key == "captcha" and any(
                    error == "This field is required." for error in errors
                ):
                    messages.error(
                        request,
                        "You must pass the reCAPTCHA test."
                    )
                else:
                    for error in errors:
                        messages.error(request, error)

    else:
        form = UserLoginForm()

    return render(
        request,
        "broker/login.html",
        {"form": form},
    )


@user_not_authenticated
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            user.is_active = True
            user.save()
            # Email activation removed
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="broker/register.html",
        context={"form": form}
    )

@login_required (login_url = "login")
def accounthistory(request):
    user = request.user

    withdrawals = Withdrawal.objects.filter(user=user)


    context = {'withdrawals':withdrawals}
    return render (request, "broker/accounthistory.html", context)

@login_required (login_url = "login")
def asset_balance(request):
    context = {}
    return render (request, "broker/asset_balance.html", context)

@login_required (login_url = "login")
def buy_plan(request):
    context = {}
    return render (request, "broker/buy-plan.html", context)

@login_required (login_url = "login")
def dashboard(request):
    context = {}
    return render (request, "broker/dashboard.html", context)

def custom_logout(request):
    logout(request)
    return redirect("dashboard")

@login_required (login_url = "login")
def account_settings(request):
    settings, created = ProfileSettings.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        action = request.POST.get("action")

        # PROFILE SETTINGS
        if action == "profile":
            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            date_of_birth = request.POST.get("date_of_birth") or None
            nationality = request.POST.get("nationality", "").strip()

            if not full_name or not email:
                messages.error(
                    request, "Full name and email are required."
                )
            elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                messages.error(request, "Enter a valid email address.")
            else:
                # Check whether another account uses this email.
                email_in_use = request.user.__class__.objects.filter(
                    email__iexact=email
                ).exclude(pk=request.user.pk).exists()

                if email_in_use:
                    messages.error(
                        request, "That email address is already in use."
                    )
                else:
                    parts = full_name.split()
                    request.user.first_name = parts[0]
                    request.user.last_name = " ".join(parts[1:])
                    request.user.email = email
                    request.user.save(
                        update_fields=["first_name", "last_name", "email"]
                    )

                    settings.phone_number = phone_number
                    settings.date_of_birth = date_of_birth
                    settings.nationality = nationality
                    settings.save()

                    messages.success(
                        request, "Profile settings updated successfully."
                    )

            return redirect("account-settings")

        # WITHDRAWAL SETTINGS
        elif action == "withdrawal":
            settings.bank_name = request.POST.get(
                "bank_name", ""
            ).strip()
            settings.account_name = request.POST.get(
                "account_name", ""
            ).strip()
            settings.account_number = request.POST.get(
                "account_number", ""
            ).strip()
            settings.swift_code = request.POST.get(
                "swift_code", ""
            ).strip()

            settings.bitcoin_address = request.POST.get(
                "bitcoin_address", ""
            ).strip()
            settings.ethereum_address = request.POST.get(
                "ethereum_address", ""
            ).strip()
            settings.litecoin_address = request.POST.get(
                "litecoin_address", ""
            ).strip()

            settings.save()

            messages.success(
                request, "Withdrawal settings saved successfully."
            )
            return redirect("account-settings")

        # CHANGE PASSWORD
        elif action == "password":
            old_password = request.POST.get("old_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get(
                "confirm_password", ""
            )

            if not request.user.check_password(old_password):
                messages.error(request, "Your old password is incorrect.")

            elif new_password != confirm_password:
                messages.error(
                    request, "The new passwords do not match."
                )

            else:
                try:
                    validate_password(new_password, request.user)
                except ValidationError as errors:
                    for error in errors:
                        messages.error(request, error)
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)

                    messages.success(
                        request, "Your password was changed successfully."
                    )

            return redirect("account-settings")

    full_name = (
        f"{request.user.first_name} {request.user.last_name}"
    ).strip()

    context = {
        "settings": settings,
        "full_name": full_name,
    }

    return render (request, "broker/account-settings.html", context)

@login_required (login_url = "login")
def myplans(request):
    context = {}
    return render (request, "broker/myplans.html", context)

@login_required (login_url = "login")
def btc(request):
    user = request.user

    withdrawals = user.withdrawals.all().order_by('-created_at')

    if request.method == 'POST':
    # Get the form data
        details = request.POST.get('details', '').strip()
        method = request.POST.get('method', '').strip()
        amount_value = request.POST.get('amount', '').strip()

        account_name = request.POST.get('account_name', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        routing_number = request.POST.get('routing_number', '').strip()
        transfer_code = request.POST.get('transfer_code', '').strip()

        # Validate amount
        try:
            amount = Decimal(amount_value)

            if not amount.is_finite() or amount <= 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid withdrawal amount.')
            return redirect('btc')

        # Save the withdrawal request
        Withdrawal.objects.create(
            user=request.user,
            details=details,
            method=method,
            amount=amount,
            account_name=account_name,
            bank_name=bank_name,
            account_number=account_number,
            routing_number=routing_number,
            transfer_code=transfer_code,
            status='Pending',
        )

        # Redirect to PIN verification AFTER saving
        return redirect('pin')

    context = {
        'withdrawal': withdrawals,
        'withdrawals': withdrawals,
    }
    return render (request, "broker/btc.html", context)

@login_required (login_url = "login")
def bank_transfer(request):
    user = request.user

    withdrawals = user.withdrawals.all().order_by('-created_at')

    if request.method == 'POST':
    # Get the form data
        details = request.POST.get('details', '').strip()
        method = request.POST.get('method', '').strip()
        amount_value = request.POST.get('amount', '').strip()

        account_name = request.POST.get('account_name', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        routing_number = request.POST.get('routing_number', '').strip()
        transfer_code = request.POST.get('transfer_code', '').strip()

        # Validate amount
        try:
            amount = Decimal(amount_value)

            if not amount.is_finite() or amount <= 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid withdrawal amount.')
            return redirect('bank_transfer')

        # Save the withdrawal request
        Withdrawal.objects.create(
            user=request.user,
            details=details,
            method=method,
            amount=amount,
            account_name=account_name,
            bank_name=bank_name,
            account_number=account_number,
            routing_number=routing_number,
            transfer_code=transfer_code,
            status='Pending',
        )

        # Redirect to PIN verification AFTER saving
        return redirect('btc')

    context = {
        'withdrawal': withdrawals,
        'withdrawals': withdrawals,
    }
    return render (request, "broker/bank_transfer.html", context)

@login_required (login_url = "login")
def deposits(request):
    context = {}
    return render (request, "broker/deposits.html", context)


@login_required (login_url = "login")
def referuser(request):
    context = {}
    return render (request, "broker/referuser.html", context)


@login_required (login_url = "login")
def support(request):
    context = {}
    return render (request, "broker/support.html", context)

@login_required (login_url = "login")
def pin(request):
    context = {}
    return render (request, "broker/pin.html", context)



@login_required (login_url = "login")
def tradinghistory(request):
    context = {}
    return render (request, "broker/tradinghistory.html", context)

@login_required (login_url = "login")
def withdraw_funds(request):
    user = request.user

    withdrawals = user.withdrawals.all().order_by('-created_at')

    if request.method == 'POST':
    # Get the form data
        details = request.POST.get('details', '').strip()
        method = request.POST.get('method', '').strip()
        amount_value = request.POST.get('amount', '').strip()

        account_name = request.POST.get('account_name', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        routing_number = request.POST.get('routing_number', '').strip()
        transfer_code = request.POST.get('transfer_code', '').strip()

        # Validate amount
        try:
            amount = Decimal(amount_value)

            if not amount.is_finite() or amount <= 0:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid withdrawal amount.')
            return redirect('withdraw-funds')

        # Save the withdrawal request
        Withdrawal.objects.create(
            user=request.user,
            details=details,
            method=method,
            amount=amount,
            account_name=account_name,
            bank_name=bank_name,
            account_number=account_number,
            routing_number=routing_number,
            transfer_code=transfer_code,
            status='Pending',
        )

        # Redirect to PIN verification AFTER saving
        return redirect('pin')

    context = {
        'withdrawal': withdrawals,
        'withdrawals': withdrawals,
    }
    return render (request, "broker/withdraw-funds.html", context)


@login_required (login_url = "login")
def withdrawals(request):
    context = {}
    return render (request, "broker/withdrawals.html", context)

@login_required (login_url = "login")
def forgot_password(request):
    context = {}
    return render (request, "broker/forgot-password.html", context)


@login_required (login_url = "login")
def processing(request):
    context = {}
    return render (request, "broker/processing.html", context)


