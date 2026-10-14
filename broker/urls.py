from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path ('login/', views.custom_login, name = "login"),
    path ('register/', views.register, name = "register"),
    path ('accounthistory/', views.accounthistory, name = "accounthistory"),
    path ('asset_balance/', views.asset_balance, name = "asset-balance"),
    path ('buy_plan/', views.buy_plan, name = "buy-plan"),
    path ('dashboard/', views.dashboard, name = "dashboard"),
    path ('deposits/', views.deposits, name = "deposits"),
    path ('referuser/', views.referuser, name = "referuser"),
    path ('support/', views.support, name = "support"),
    path ('tradinghistory/', views.tradinghistory, name = "tradinghistory"),
    path ('withdraw_funds/', views.withdraw_funds, name = "withdraw-funds"),
    path ('withdrawals/', views.withdrawals, name = "withdrawals"),
    path ('account_settings/', views.account_settings, name = "account-settings"),
    path ('logout/', views.custom_logout, name = "logout"),
    path ('myplans/', views.myplans, name = "myplans"),
    path ('forgot_password/', views.forgot_password, name = "forgot-password"),
    path ('btc/', views.btc, name = "btc"),
    path ('bank_transfer/', views.bank_transfer, name = "bank_transfer"),
    path ('pin/', views.pin, name = "pin"),
    path ('processing/', views.processing, name = "processing"),


 ]