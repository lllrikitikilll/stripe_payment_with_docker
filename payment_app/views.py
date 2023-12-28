import stripe
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from payment_app.models import Item, Order, Discount
from payment_stripe.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY, YOUR_DOMAIN
from payment_app.stripe_utils import get_item

stripe.api_key = STRIPE_SECRET_KEY


class CreateCheckoutSessionItemView(View):
    """Получение сессии на покупку одного Item"""
    DOMAIN = YOUR_DOMAIN

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        item = Item.objects.get(pk=self.kwargs['pk'])
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=get_item([item]),
            mode='payment',
            success_url=self.DOMAIN + '/success',
            cancel_url=self.DOMAIN + '/cancel',
        )
        return JsonResponse({'id': checkout_session.id})


class CreateCheckoutSessionOrderView(View):
    """Получение сессии на покупку одного группы Item по url /buy_order/<int:pk>/"""
    DOMAIN = YOUR_DOMAIN

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        order = Order.objects.get(pk=self.kwargs['pk'])
        data_for_checkout_session = {
            'payment_method_types': ['card'],
            'line_items': get_item(order.items.all()),
            'mode': 'payment',
            'success_url': self.DOMAIN + '/success',
            'cancel_url': self.DOMAIN + '/cancel',
        }
        # Если есть купон валидный добавить его к параметрам
        if order.discount and stripe.Coupon.retrieve(order.discount.coupon_id).valid:
            data_for_checkout_session['discounts'] = [{'coupon': order.discount.coupon_id}]
        elif order.discount:
            # Иначе сделать недействительным
            Discount.objects.filter(pk=order.discount.id).update(valid=False)
            Order.objects.filter(pk=order.id).update(discount=None)
        checkout_session = stripe.checkout.Session.create(**data_for_checkout_session)
        return JsonResponse({'id': checkout_session.id})


class OrderTemplateView(TemplateView):
    """Возвращает страницу с Item"""
    template_name = 'payment_app/order.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.get(pk=self.kwargs['pk'])
        context['public_key'] = STRIPE_PUBLIC_KEY
        return context


class ItemTemplateView(TemplateView):
    """Возвращает страницу с Order (группа item)"""
    template_name = 'payment_app/item.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['item'] = Item.objects.get(pk=self.kwargs['pk'])
        context['public_key'] = STRIPE_PUBLIC_KEY
        return context


class SuccessTemplateView(TemplateView):
    """Возвращает страницу удачной оплаты"""
    template_name = 'payment_app/success.html'


class CancelTemplateView(SuccessTemplateView):
    """Возвращает страницу с ошибкой оплаты"""
    template_name = 'payment_app/cancel.html'
