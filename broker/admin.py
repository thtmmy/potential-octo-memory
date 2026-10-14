from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register (Deposit)
admin.site.register (Wallet)

@admin.register(ProfileSettings)
class ProfileSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "nationality",
        "bank_name",
        "account_name",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
        "bank_name",
        "account_name",
    )

    list_filter = ("nationality", "bank_name")
    readonly_fields = ("updated_at",)
    ordering = ("-updated_at",)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'amount',
        'method',
        'status',
        'reference',
        'created_at',
    )

    list_filter = (
        'status',
        'method',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
        'account_name',
        'bank_name',
        'account_number',
    )

    list_editable = ('status',)

    readonly_fields = (
        'reference',
        'created_at',
        'updated_at',
    )

    ordering = ('-created_at',)

admin.site.register (Pin)