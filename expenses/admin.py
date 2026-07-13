from django.contrib import admin
from .models import Category, Notification, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    ordering = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'transaction_type', 'category', 'user', 'date', 'created_at')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'amount', 'transaction_type', 'category', 'user')
        }),
        ('Details', {
            'fields': ('description', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'message', 'user', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
