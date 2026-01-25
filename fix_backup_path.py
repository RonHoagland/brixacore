import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform_core.settings")
django.setup()

from core.models import Preference
from backup.models import BackupSettings

# Path validation
PROJECT_ROOT = Path(os.getcwd())
# Use sibling directory to avoid "inside app dir" validation error
SAFE_BACKUP_PATH = PROJECT_ROOT.parent / "Brixa_Backups"
SAFE_BACKUP_PATH.mkdir(exist_ok=True)

print(f"Setting safe backup path: {SAFE_BACKUP_PATH}")

# 1. Update Core Preference
try:
    pref = Preference.objects.get(key="backup_storage_path")
    pref.value = str(SAFE_BACKUP_PATH)
    pref.save()
    print("✓ Updated 'backup_storage_path' Preference")
except Preference.DoesNotExist:
    print("✗ Preference 'backup_storage_path' not found")

# 2. Update BackupSettings (Singleton)
try:
    settings = BackupSettings.get_settings()
    settings.backup_path = str(SAFE_BACKUP_PATH)
    settings.save()
    print("✓ Updated BackupSettings singleton")
except Exception as e:
    print(f"✗ Failed to update BackupSettings: {e}")

# Verify
print(f"Current Backup Configuration: {BackupSettings.get_settings().backup_path}")
