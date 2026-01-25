from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.management import call_command
from .models import Backup, BackupSettings
from core.utils import apply_sorting

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def backup_dashboard_view(request):
    settings = BackupSettings.get_settings()
    backups = Backup.objects.all()
    
    # Sorting
    backups, sort_field, sort_dir = apply_sorting(
        backups, 
        request, 
        allowed_fields=['backup_timestamp', 'backup_id', 'status', 'backup_type', 'database_size_bytes'], 
        default_sort='backup_timestamp', 
        default_dir='desc'
    )

    return render(request, "backup/dashboard.html", {
        "settings": settings,
        "backups": backups,
        "current_sort": sort_field,
        "current_dir": sort_dir
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def trigger_backup_view(request):
    if request.method == "POST":
        try:
            # Note: This is synchronous and might block
            call_command('backup', type='manual')
            messages.success(request, "Backup completed successfully.")
        except Exception as e:
            messages.error(request, f"Backup failed: {str(e)}")
            
    return redirect('backup_dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def restore_backup_view(request, backup_id):
    # restoration logic would go here
    # For now, just a placeholder or call a restore command if available
    pass
