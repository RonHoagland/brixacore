from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Preference

class Command(BaseCommand):
    help = 'Initializes the standard set of system preferences.'

    def handle(self, *args, **options):
        self.stdout.write('Initializing system preferences...')
        
        system_user, _ = User.objects.get_or_create(username='system', defaults={'is_active': False})
        
        # Define standard preferences
        # (key, value, type, name, description)
        defaults = [
            # General / Company
            ('company_name', 'BrixaWares', 'string', 'Company Name', 'Name of the organization using the platform'),
            ('company_address', '', 'string', 'Company Address', 'Physical address for reports/invoices'),
            ('company_phone', '', 'string', 'Company Phone', 'Contact number for reports'),
            ('company_email', '', 'string', 'Company Email', 'Contact email for system notifications'),
            ('company_website', '', 'string', 'Company Website', 'Main website URL'),

            # System / UI
            ('site_title', 'BrixaWares Platform', 'string', 'Site Title', 'Browser tab title'),
            ('ui_theme_mode', 'light', 'string', 'Default Theme Mode', 'Default UI theme (light/dark)'),
            ('ui_footer_text', '© 2026 BrixaWares', 'string', 'Footer Text', 'Text displayed in the application footer'),
            ('ui_rows_per_page', '20', 'integer', 'Rows Per Page', 'Default number of items per list page'),

            # Security
            ('security_session_timeout', '60', 'integer', 'Session Timeout', 'Minutes of inactivity before logout'),
            ('security_password_expiry', '90', 'integer', 'Password Expiry Days', 'Days before password change is required (0 to disable)'),
            ('security_mfa_required', 'false', 'boolean', 'Require MFA', 'Enforce Multi-Factor Authentication for all users'),

            # Email Configuration
            ('email_from_address', 'noreply@brixawares.com', 'string', 'From Email Address', 'Default sender address for system emails'),
            ('email_smtp_host', 'smtp.example.com', 'string', 'SMTP Host', 'Mail server hostname'),
            ('email_smtp_port', '587', 'integer', 'SMTP Port', 'Mail server port'),
            ('email_use_tls', 'true', 'boolean', 'Use TLS', 'Enable Transport Layer Security for email'),
            
            # Backup & Retention
            ('backup_retention_days', '30', 'integer', 'Backup Retention (Days)', 'Number of days to keep automated backups'),
            ('backup_storage_path', '/var/backups/brixa', 'path', 'Backup Storage Path', 'Absolute path for local backup storage'),
            ('audit_log_retention_days', '365', 'integer', 'Audit Log Retention (Days)', 'Days to keep audit logs before archiving'),
        ]

        created_count = 0
        updated_count = 0

        for key, val, dtype, name, desc in defaults:
            obj, created = Preference.objects.get_or_create(
                key=key,
                defaults={
                    'value': val,
                    'default_value': val,
                    'data_type': dtype,
                    'name': name,
                    'description': desc,
                    'created_by': system_user,
                    'updated_by': system_user
                }
            )
            
            if created:
                created_count += 1
            else:
                # Optional: Update metadata if it changed, but don't overwrite user-set values
                updated = False
                if obj.name != name: obj.name = name; updated = True
                if obj.description != desc: obj.description = desc; updated = True
                if obj.data_type != dtype: obj.data_type = dtype; updated = True
                
                if updated:
                    obj.save()
                    updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully processed preferences. Created: {created_count}, Updated: {updated_count}'))
