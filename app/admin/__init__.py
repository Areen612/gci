from django.contrib import admin

from .invoice_admin import *
from .customer_admin import *
from .lineitem_admin import *
from .seller_admin import *
from .item_admin import *

# Customize admin site titles
admin.site.site_header = "GCI Administration"
admin.site.site_title = "GCI Admin Portal"
admin.site.index_title = "Welcome to GCI Admin"