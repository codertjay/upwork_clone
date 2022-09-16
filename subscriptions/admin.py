from django.contrib import admin

from .models import UserSubscription
from plans.models import Plan

admin.site.register(Plan)
admin.site.register(UserSubscription)
