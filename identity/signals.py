from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

USER_LIMIT = 5

@receiver(pre_save, sender=User)
def check_user_limit(sender, instance, **kwargs):
    """
    Enforce Lite version user limit.
    Allow updates to existing users, but block creation of new ones if limit reached.
    """
    if not instance.pk:  # Only for new users
        current_count = User.objects.count()
        if current_count >= USER_LIMIT:
            raise ValidationError(f"Lite Version Restriction: Maximum {USER_LIMIT} users allowed.")
