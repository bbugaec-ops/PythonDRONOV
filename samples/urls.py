from django.urls import path

from .views import index, by_rubric, add_and_save, add_to_cart, show_cart, clear_cart, checkout,order_request,remove_from_cart

urlpatterns = [
    path('add/', add_and_save, name='add'),
    path('<int:rubric_id>/', by_rubric, name='by_rubric'),
    path('order_request/<int:pk>/', order_request, name='order_request'),
    path('', index, name='index'),
    path('add_to_cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/', show_cart, name='cart'),
    path('clear/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('cart/remove/<int:pk>/', remove_from_cart, name='remove_from_cart'),

]
