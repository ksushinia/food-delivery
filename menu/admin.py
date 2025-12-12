from django.contrib import admin
from .models import PromoCode
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug') # Что показывать в списке
    prepopulated_fields = {'slug': ('name',)} # Автоматически заполнять slug из имени

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available') # Столбцы в таблице
    list_filter = ('category', 'is_available') # Фильтр справа (очень удобно!)
    search_fields = ('name', 'description') # Строка поиска
    list_editable = ('is_available', 'price')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Не показывать пустые строки для новых товаров
    readonly_fields = ('price',) # Чтобы менеджер не мог менять цену задним числом

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('first_name', 'phone_number', 'address')
    inlines = [OrderItemInline] # <-- Вот эта магия подключает товары
    readonly_fields = ('total_price', 'created_at')

    # Удобные действия: "Пометить как Доставлено" прямо из списка
    actions = ['mark_as_delivered']

    @admin.action(description="Обновить статус на 'Доставлен'")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_until', 'is_active')