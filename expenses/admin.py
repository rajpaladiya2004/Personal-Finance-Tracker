from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'transaction_type', 'category', 'date', 'created_at')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('title', 'description')
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'amount', 'transaction_type', 'category')
        }),
        ('Details', {
            'fields': ('description', 'date')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
