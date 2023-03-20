from django.contrib import admin
from .models import *


admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DevisItem)
admin.site.register(Profile)
admin.site.register(BillingAddress)
admin.site.register(ShippingAddress)
admin.site.register(Annonce)
admin.site.register(Annonce_responde)
admin.site.register(SignaledItems)
