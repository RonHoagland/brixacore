"""
Identity models: Roles, User Roles, and User Profile.

Implements Lite role set (Owner/Admin, Worker/User, Read-Only) and provides
infrastructure for permission checks across the platform.
"""

from django.conf import settings
from django.db import models

from core.models import BaseModel


class Role(BaseModel):
	"""System role definition (Lite: Owner, Worker, Read-Only)."""

	key = models.CharField(
		max_length=100,
		unique=True,
		help_text="Machine-friendly role key (e.g., owner_admin, worker_user, read_only)",
	)

	name = models.CharField(
		max_length=200,
		help_text="Human-friendly role name",
	)

	description = models.TextField(
		blank=True,
		help_text="Purpose and scope of this role",
	)

	is_system = models.BooleanField(
		default=True,
		help_text="True for system-defined roles (Owner, Worker, Read-Only)",
	)

	class Meta:
		ordering = ["name"]
		indexes = [
			models.Index(fields=["key"]),
			models.Index(fields=["is_active"]),
		]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.name} ({self.key})"


class UserRole(BaseModel):
	"""Assignment of a role to a user."""

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="user_roles",
		help_text="User receiving the role",
	)

	role = models.ForeignKey(
		Role,
		on_delete=models.PROTECT,
		related_name="assigned_users",
		help_text="Assigned role",
	)

	class Meta:
		unique_together = [("user", "role")]
		indexes = [
			models.Index(fields=["user", "role"]),
		]
		ordering = ["user__username"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.user} → {self.role}"


class UserProfile(BaseModel):
	"""Additional profile data for users (non-auth fields)."""

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="profile",
		help_text="User owning this profile",
	)

	display_name = models.CharField(
		max_length=200,
		blank=True,
		help_text="Preferred display name",
	)

	time_zone = models.CharField(
		max_length=64,
		blank=True,
		help_text="IANA time zone name (e.g., UTC, America/New_York)",
	)

	class Meta:
		ordering = ["user__username"]
		indexes = [
			models.Index(fields=["user"]),
		]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return self.display_name or self.user.get_username()
