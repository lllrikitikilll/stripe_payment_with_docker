from django.urls import path
from payment_app import views

urlpatterns = [
    path('buy/<int:pk>'),
    path('item/<int:pk>'),
    path('buy_order/<int:pk>'),
    path('order/<int:pk>'),
]