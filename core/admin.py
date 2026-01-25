"""
Core Admin - Configuration interface for System Configuration components
"""

from django.contrib import admin
from .models import Preference, ValueList, ValueListItem


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'value', 'data_type', 'is_editable', 'is_active')
    list_filter = ('data_type', 'is_editable', 'is_active')
    search_fields = ('key', 'name', 'description')
    readonly_fields = ('id', 'created_at', 'created_by', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Identification', {
            'fields': ('key', 'name', 'description')
        }),
        ('Value', {
            'fields': ('value', 'default_value', 'data_type')
        }),
        ('Constraints', {
            'fields': ('is_editable', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ValueList)
class ValueListAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'is_active')
    search_fields = ('key', 'name', 'description')
    readonly_fields = ('id', 'created_at', 'created_by', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Identification', {
            'fields': ('key', 'name', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ValueListItem)
class ValueListItemAdmin(admin.ModelAdmin):
    list_display = ('value_list', 'value', 'display_label', 'sort_order', 'is_active')
    list_filter = ('value_list', 'is_active')
    search_fields = ('value', 'display_label', 'description')
    readonly_fields = ('id', 'created_at', 'created_by', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Association', {
            'fields': ('value_list',)
        }),
        ('Value', {
            'fields': ('value', 'display_label', 'description')
        }),
        ('Display', {
            'fields': ('sort_order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'created_by', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
