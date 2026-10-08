from django.contrib import admin
from .models import (
    UserProfile,
    Reservation,
    MenuCategory,
    MenuItem,
    RestaurantTable,
    TableSession,
    Order,
    OrderItem,
    Bill,
    Payment,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "is_email_verified", "created_at")
    search_fields = ("user__email", "user__first_name", "phone_number")
    list_filter = ("is_email_verified", "created_at")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone_number", "date", "time", "guests", "seating_preference", "status", "created_at")
    list_filter = ("status", "date", "seating_preference")
    search_fields = ("name", "email", "phone_number", "id")
    date_hierarchy = "date"


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "is_active", "preparation_time")
    list_filter = ("category", "is_available", "is_active")
    search_fields = ("name", "description")
    list_editable = ("is_available", "is_active")


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "capacity", "status", "is_active", "qr_token")
    list_filter = ("status", "is_active")
    search_fields = ("table_number", "qr_token")


@admin.register(TableSession)
class TableSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "table", "guest_name", "guest_count", "status", "opened_at", "closed_at")
    list_filter = ("status", "opened_at")
    search_fields = ("guest_name", "table__table_number")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("unit_price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "source", "status", "created_at")
    list_filter = ("source", "status", "created_at")
    search_fields = ("id", "session__table__table_number")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "menu_item", "quantity", "unit_price", "status")
    list_filter = ("status", "created_at")
    search_fields = ("menu_item__name", "order__id")


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "subtotal", "tax", "discount", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "session__table__table_number")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "bill", "amount", "payment_method", "status", "created_at")
    list_filter = ("payment_method", "status", "created_at")
    search_fields = ("id", "transaction_id", "bill__id")
