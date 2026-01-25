"""Admin registrations for Identity components."""

from django.contrib import admin

from .models import Role, UserProfile, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ("name", "key", "is_system", "is_active")
	list_filter = ("is_system", "is_active")
	search_fields = ("name", "key", "description")
	readonly_fields = ("id", "created_at", "created_by", "updated_at", "updated_by")

	def save_model(self, request, obj, form, change):
		if not change:  # Creating new object
			obj.created_by = request.user
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "is_active")
	list_filter = ("role", "is_active")
	search_fields = ("user__username", "role__name", "role__key")
	readonly_fields = ("id", "created_at", "created_by", "updated_at", "updated_by")

	def save_model(self, request, obj, form, change):
		if not change:  # Creating new object
			obj.created_by = request.user
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "display_name", "time_zone", "is_active")
	search_fields = ("user__username", "display_name")
	readonly_fields = ("id", "created_at", "created_by", "updated_at", "updated_by")

	def save_model(self, request, obj, form, change):
		if not change:  # Creating new object
			obj.created_by = request.user
		obj.updated_by = request.user
		super().save_model(request, obj, form, change)
