from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.db import models
# Create your models here.
import uuid
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Deposit(models.Model):
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    deposit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00")
    )

    profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00")
    )

    withdrawals = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00")
    )

    account_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00")
    )

    investment_plans = models.CharField(
        max_length=200,
        default="Silver"
    )

    active_investment_plans = models.CharField(
        max_length=200,
        default="Unverified"
    )

    currency = models.CharField(
        max_length=10,
        default="$"
    )

    def save(self, *args, **kwargs):
        self.account_balance = self.deposit + self.profit
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name or self.user or "Deposit")
    
class ProfileSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile_settings"
    )

    # Profile settings
    phone_number = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    # Bank withdrawal settings
    bank_name = models.CharField(max_length=150, blank=True)
    account_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    swift_code = models.CharField(max_length=30, blank=True)

    # Cryptocurrency withdrawal settings
    bitcoin_address = models.CharField(max_length=255, blank=True)
    ethereum_address = models.CharField(max_length=255, blank=True)
    litecoin_address = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"
    

class Wallet (models.Model):
    user = models.OneToOneField (User, null = True, blank = True, on_delete = models.CASCADE)
    name = models.CharField (max_length = 200,  null = True)
    btc = models.CharField (max_length = 200, default = "Generating..",)
    usdt = models.CharField (max_length = 200, default = "Generating..",)

    def __str__(self):
        return str(self.name)
    




class Withdrawal(models.Model):

    # Withdrawal methods
    WITHDRAWAL_METHODS = [
        ('BTC', 'Bitcoin (BTC)'),
        ('USDT (BEP20)', 'USDT (BEP20)'),
        ('Bank Transfer', 'Bank Transfer'),
    ]

    # Withdrawal statuses
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ]

    # User who requested the withdrawal
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )

    # Withdrawal amount
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Withdrawal method
    method = models.CharField(
        max_length=30,
        choices=WITHDRAWAL_METHODS
    )

    # Cryptocurrency wallet address
    details = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    # Bank transfer details
    account_name = models.CharField(
        max_length=150,
        blank=True,
        default=''
    )

    bank_name = models.CharField(
        max_length=150,
        blank=True,
        default=''
    )

    account_number = models.CharField(
        max_length=50,
        blank=True,
        default=''
    )

    routing_number = models.CharField(
        max_length=50,
        blank=True,
        default=''
    )

    # Optional transfer reference/code
    transfer_code = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    # Unique withdrawal reference
    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # Withdrawal status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # Optional admin notes
    admin_note = models.TextField(
        blank=True,
        default=''
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.method} - "
            f"{self.amount} - "
            f"{self.status}"
        )
    
class Pin (models.Model):
    user = models.OneToOneField (User, null = True, blank = True, on_delete = models.CASCADE)
    name = models.CharField (max_length = 200,  null = True)
    pin = models.CharField (max_length = 200, null = True, default = "1991")


    def __str__(self):
        return str(self.name)
