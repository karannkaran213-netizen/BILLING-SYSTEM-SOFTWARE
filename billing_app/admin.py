from django.contrib import admin
from .models import Menu, Order, OrderItem, Expense


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_available', 'created_at']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_available']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'total_amount', 'status', 'created_at', 'total_items']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price', 'subtotal']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'menu_item__name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'category', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['description']
    date_hierarchy = 'date'
