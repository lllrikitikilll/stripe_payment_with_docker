from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from stripe import Coupon, TaxRate


class Item(models.Model):
    """Модель отдельных продуктов"""

    class Currency(models.TextChoices):
        EUR = 'EUR'
        USD = 'USD'

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    tax = models.ForeignKey('Tax', on_delete=models.SET_NULL, default=None, null=True)

    def get_price(self):
        return int(self.price) / 100

    def __str__(self):
        return f'{self.name:.7} {self.price}'


class Order(models.Model):
    """Модель корзины"""
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True)

    def get_items(self):
        return self.items.all()

    def __str__(self):
        return f'id{self.id} | {self.items.count()} шт'


class Tax(models.Model):
    """Модель налоговой ставки"""

    id = models.CharField(max_length=20, primary_key=True)
    inclusive = models.BooleanField(default=False)
    display_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    country = models.CharField(max_length=255, default=None, null=True, blank=True)
    percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    def save(self, *args, **kwargs):
        tax_rate = TaxRate.create(
            inclusive=self.inclusive,
            display_name=self.display_name,
            active=self.active,
            country=self.country,
            percentage=self.percentage,
        )

        self.id = tax_rate.id
        self.inclusive = tax_rate.inclusive
        self.display_name = tax_rate.display_name
        self.active = tax_rate.active
        self.country = tax_rate.country
        self.percentage = tax_rate.percentage

        return super().save(self, args, kwargs)

    def __str__(self):
        return f'{self.display_name} | {self.percentage}%'


class Discount(models.Model):
    """Модель скидочного купона. Идет обращение к внешнему сервису Stirpe"""

    id = models.CharField(max_length=20, primary_key=True)
    amount_off = models.IntegerField(null=True, validators=[MinValueValidator(0)], blank=True)
    created = models.CharField(max_length=20)
    duration = models.CharField(max_length=25, default="repeating")
    duration_in_months = models.IntegerField(null=True, default=1)
    max_redemptions = models.IntegerField(null=True, default=None, blank=True)
    name = models.CharField(max_length=255, null=True)
    percent_off = models.DecimalField(max_digits=5, decimal_places=1)
    valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not int(self.percent_off):
            self.id = 0
            self.created = 0
            self.amount_off = None
            self.duration_in_months = 3600
            self.max_redemptions = None
            return super().save(self)

        # Если есть скидка - сохраняем информацию о купоне
        coupon = Coupon.create(
            amount_off=self.amount_off,
            duration=self.duration,
            duration_in_months=self.duration_in_months,
            max_redemptions=self.max_redemptions,
            name=self.name,
            percent_off=self.percent_off,

        )
        self.id = coupon.id
        self.created = coupon.created
        self.valid = coupon.valid
        self.amount_off = coupon.amount_off
        self.duration = coupon.duration
        self.duration_in_months = coupon.duration_in_months
        self.max_redemptions = coupon.max_redemptions
        self.name = coupon.name
        self.percent_off = coupon.percent_off

        return super().save(self, args, kwargs)

    def __str__(self):
        return f'{self.name}'