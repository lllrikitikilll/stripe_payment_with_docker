from django.urls import path
from payment_app import views


urlpatterns = [
    path('buy/<int:pk>/', views.CreateCheckoutSessionItemView.as_view(), name='create-checkout-session-item'),
    path('item/<int:pk>/', views.ItemTemplateView.as_view(), name='item-template-page'),
    path('buy_order/<int:pk>/', views.CreateCheckoutSessionOrderView.as_view(), name='create-checkout-session-order'),
    path('order/<int:pk>/', views.OrderTemplateView.as_view(), name='order-template-page'),
    path('success/', views.SuccessTemplateView.as_view(), name='success'),
    path('cancel/', views.CancelTemplateView.as_view(), name='cancel')
]