"""
Backup & Restore Infrastructure Models

Implements backup scheduling, metadata tracking, and restore history
per Platform Core Backup/Restore specification.

Provides:
- BackupSettings: Global preferences (path, schedule, retention)
- Backup: Metadata for individual backup instances
- BackupLog: Execution history and failure tracking
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from pathlib import Path
from core.models import BaseModel


class BackupSettings(BaseModel):
    """
    Global backup preferences and configuration.
    
    Singleton model - only one instance should exist.
    Stores:
    - Backup storage path (validated)
    - Daily schedule time (HH:MM)
    - Retention count (minimum 5)
    """
    
    backup_path = models.CharField(
        max_length=500,
        default=r'C:\ProgramData\BrixaWares\Backups',
        help_text="Absolute path where backups are stored. Must be writable."
    )
    
    schedule_time = models.TimeField(
        default='02:00',
        help_text="Time of day (local) when automatic backup runs (HH:MM)"
    )
    
    retention_count = models.IntegerField(
        default=10,
        help_text="Number of backups to keep (minimum 5)"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable automatic backups"
    )
    
    class Meta:
        verbose_name_plural = "Backup Settings"
    
    def clean(self):
        """Validate backup path and retention settings."""
        # Validate retention count
        if self.retention_count < 5:
            raise ValidationError(
                {'retention_count': 'Retention count must be at least 5.'}
            )
        
        # Validate backup path exists or can be created
        try:
            path = Path(self.backup_path)
            path.mkdir(parents=True, exist_ok=True)
            
            # Test write permission
            test_file = path / '.write_test'
            test_file.write_text('test')
            test_file.unlink()
        except (OSError, PermissionError) as e:
            raise ValidationError(
                {'backup_path': f'Backup path is not writable: {str(e)}'}
            )
        
        # Ensure path is not inside installation directory
        install_dir = Path(__file__).resolve().parent.parent
        try:
            Path(self.backup_path).relative_to(install_dir)
            raise ValidationError(
                {'backup_path': 'Backup path cannot be inside the application installation directory.'}
            )
        except ValueError:
            # Good - path is outside install directory
            pass
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        # Get the first (and should be only) instance
        obj = cls.objects.first()
        if obj:
            return obj
        
        # Create default if none exists
        from django.contrib.auth.models import User
        system_user, _ = User.objects.get_or_create(username='system')
        
        obj = cls.objects.create(
            backup_path=str(Path.home() / 'BrixaWares_Backups'),
            schedule_time='02:00',
            retention_count=10,
            is_enabled=True,
            created_by=system_user,
            updated_by=system_user,
        )
        return obj
    
    def __str__(self):
        return f"Backup Settings (Path: {self.backup_path}, Time: {self.schedule_time})"


class Backup(BaseModel):
    """
    Metadata record for a completed backup.
    
    Tracks:
    - Backup timestamp and location
    - Application and database versions
    - File/document count
    - Success status and failure reason
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]
    
    # Backup identity
    backup_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique backup identifier (timestamp-based)"
    )
    
    backup_path = models.CharField(
        max_length=500,
        help_text="Absolute path to backup folder"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current backup status"
    )
    
    # Timing
    backup_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When backup was created"
    )
    
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup process started"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backup process completed"
    )
    
    # Version tracking
    app_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="BrixaWares version"
    )
    
    schema_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Database schema version"
    )
    
    database_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="PostgreSQL/database version"
    )
    
    install_mode = models.CharField(
        max_length=20,
        default='solo',
        choices=[('solo', 'Solo'), ('multi', 'Multi-user')],
        help_text="Installation mode at time of backup"
    )
    
    # Content tracking
    database_size_bytes = models.BigIntegerField(
        default=0,
        help_text="Size of database dump in bytes"
    )
    
    files_size_bytes = models.BigIntegerField(
        default=0,
        help_text="Size of files archive in bytes"
    )
    
    file_count = models.IntegerField(
        default=0,
        help_text="Number of files/documents backed up"
    )
    
    # Failure tracking
    failure_reason = models.TextField(
        blank=True,
        help_text="Human-readable reason for backup failure"
    )
    
    # Backup type
    backup_type = models.CharField(
        max_length=20,
        default='scheduled',
        choices=[
            ('scheduled', 'Scheduled'),
            ('manual', 'Manual'),
            ('pre_upgrade', 'Pre-Upgrade'),
        ],
        help_text="Type of backup (automatic, manual, pre-upgrade)"
    )
    
    class Meta:
        ordering = ['-backup_timestamp']
        indexes = [
            models.Index(fields=['-backup_timestamp']),
            models.Index(fields=['status']),
        ]
    
    def duration_seconds(self):
        """Get backup duration in seconds."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds()
        return None
    
    def is_recent_failure(self):
        """Check if this is the most recent backup and it failed."""
        latest = Backup.objects.order_by('-backup_timestamp').first()
        return latest == self and self.status == 'failed'
    
    def __str__(self):
        return f"Backup {self.backup_id} ({self.status}) - {self.backup_timestamp}"


class BackupLog(BaseModel):
    """
    Audit trail of backup and restore operations.
    
    Tracks:
    - Operation type (backup, restore, cleanup)
    - Status and messages
    - User who initiated (if manual)
    """
    
    OPERATION_CHOICES = [
        ('backup', 'Backup'),
        ('restore', 'Restore'),
        ('verify', 'Verify'),
        ('cleanup', 'Cleanup'),
        ('schedule_check', 'Schedule Check'),
    ]
    
    backup = models.ForeignKey(
        Backup,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        help_text="Related backup (if any)"
    )
    
    operation = models.CharField(
        max_length=20,
        choices=OPERATION_CHOICES,
        help_text="Type of backup operation"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('info', 'Info'),
        ],
        default='info',
        help_text="Operation result status"
    )
    
    message = models.TextField(
        blank=True,
        help_text="Detailed operation message/error"
    )
    
    log_timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When operation was logged"
    )
    
    duration_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Operation duration in seconds"
    )
    
    initiated_by = models.CharField(
        max_length=255,
        default='system',
        help_text="Who/what initiated (username or 'system')"
    )
    
    class Meta:
        ordering = ['-log_timestamp']
        indexes = [
            models.Index(fields=['-log_timestamp']),
            models.Index(fields=['operation', '-log_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.operation} - {self.status} ({self.log_timestamp})"
