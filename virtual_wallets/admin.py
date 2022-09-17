from django.contrib import admin

# Register your models here.
from virtual_wallets.models import Wallet

admin.site.register(Wallet)
