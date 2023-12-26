import decimal

from django.contrib import admin
from django.db.models import Sum
from payment_app.models import Item, Order, Discount, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'tax']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'discount', 'order_count', 'order_sum', 'percent_off', 'order_sum_with_discount']
    list_display_links = ['id', 'order_sum']

    @staticmethod
    def order_count(obj):
        return obj.items.count()

    @staticmethod
    def order_sum(obj):
        return obj.items.aggregate(res=Sum("price"))['res'] / 100

    @staticmethod
    def percent_off(obj):
        return obj.discount.percent_off

    @staticmethod
    def order_sum_with_discount(obj):
        sum = decimal.Decimal(OrderAdmin.order_sum(obj))
        return sum - sum * (obj.discount.percent_off / 100)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent_off', 'valid')
    list_display_links = ['name']
    readonly_fields = ('coupon_id', 'created')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_id', 'display_name', 'percentage')
    readonly_fields = ('tax_id',)
