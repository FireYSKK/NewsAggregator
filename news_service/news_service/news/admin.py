from django.contrib import admin
from . models import Headline, Transaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Headline)