from django.contrib.admin.sites import AlreadyRegistered
from django.db.models.loading import get_model
from django.contrib import admin

from getpaid.admin import PaymentAdmin

from .models import Order, Payment
try:
    admin.site.register(Payment, PaymentAdmin)
except AlreadyRegistered:
    pass
admin.site.register(Order)
