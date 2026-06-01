from django.contrib import admin
from .models import Bd, Rubric, Order

class BdAdmin(admin.ModelAdmin):
    # ТУТ Я ДОДАВ 'old_price' ТА 'stock_status'
    list_display = ('img_preview', 'title', 'price', 'old_price', 'stock', 'stock_status', 'published', 'rubric')
    list_display_links = ('img_preview', 'title')

    # Дозволяємо редагувати стару ціну прямо в списку
    list_editable = ('price', 'old_price', 'stock', 'rubric')
    search_fields = ('title', 'content')
    list_filter = ('rubric', 'published')
    list_per_page = 20

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'phone',
        'total_price',
        'status',
        'created_at'
    )
    list_editable = ('status',)
    list_filter = ('status', 'delivery_service', 'region', 'created_at')
    search_fields = ('last_name', 'phone', 'city', 'street')

    fieldsets = (
        ('Контактні дані', {
            'fields': ('last_name', 'first_name', 'middle_name', 'email', 'phone')
        }),
        ('Адреса доставки', {
            'fields': ('region', 'city', 'street', 'delivery_service', 'department'),
        }),
        ('Інформація про замовлення', {
            'fields': ('status', 'items', 'total_price')
        }),
    )
    readonly_fields = ('created_at',)
    list_per_page = 15

admin.site.register(Order, OrderAdmin)
admin.site.register(Bd, BdAdmin)
admin.site.register(Rubric)