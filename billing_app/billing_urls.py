from django.urls import path
from . import views

urlpatterns = [
    # Billing Interface
    path('', views.billing_index, name='billing_index'),
    
    # Cart Operations
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/get/', views.get_cart, name='get_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Order Operations
    path('order/create/', views.create_order, name='create_order'),
    path('bill/<int:order_id>/', views.view_bill, name='view_bill'),
    path('bill/<int:order_id>/pay/', views.pay_now, name='pay_now'),
    path('bill/<int:order_id>/qr/', views.generate_qr, name='generate_qr'),
]

