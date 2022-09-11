from django.contrib import admin

from .models import Wallet, Subscription, UserSubscription

admin.site.register(Wallet)
admin.site.register(Subscription)
admin.site.register(UserSubscription)
