"""
Database backup management command.

Creates a backup of:
- PostgreSQL database (logical dump)
- File storage (documents, uploads)
- Metadata (versions, timestamp, etc.)

Backup bundle structure:
  backup_YYYYMMDD_HHMMSS/
    ├── database.sql.gz
    ├── files.tar.gz
    └── metadata.json
"""

import os
import json
import gzip
import shutil
import tarfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import connections
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User

from backup.models import Backup, BackupSettings, BackupLog


class Command(BaseCommand):
    help = 'Create a complete backup of database and files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Override default backup path',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['scheduled', 'manual', 'pre_upgrade'],
            default='manual',
            help='Type of backup',
        )
        parser.add_argument(
            '--no-cleanup',
            action='store_true',
            help='Do not clean up old backups after completion',
        )
    
    def handle(self, *args, **options):
        # Get settings
        try:
            settings_obj = BackupSettings.get_settings()
        except Exception as e:
            raise CommandError(f"Failed to load backup settings: {str(e)}")
        
        if not settings_obj.is_enabled:
            self.stdout.write(self.style.WARNING('Backups are disabled'))
            return
        
        # Determine backup path
        backup_root = Path(options.get('path') or settings_obj.backup_path)
        
        try:
            backup_root.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise CommandError(f"Cannot access backup path: {str(e)}")
        
        # Create backup folder with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"backup_{timestamp}"
        backup_folder = backup_root / backup_id
        
        try:
            backup_folder.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise CommandError(f"Cannot create backup folder: {str(e)}")
        
        # Create backup record
        system_user, _ = User.objects.get_or_create(username='system')
        backup = Backup.objects.create(
            backup_id=backup_id,
            backup_path=str(backup_folder),
            status='in_progress',
            backup_type=options['type'],
            start_time=timezone.now(),
            app_version=self._get_app_version(),
            schema_version=self._get_schema_version(),
            database_version=self._get_database_version(),
            created_by=system_user,
            updated_by=system_user,
        )
        
        start_time = timezone.now()
        success = False
        error_message = None
        
        try:
            # Backup database
            self.stdout.write('Backing up database...')
            db_path, db_size = self._backup_database(backup_folder)
            backup.database_size_bytes = db_size
            
            # Backup files
            self.stdout.write('Backing up files...')
            files_path, files_size, file_count = self._backup_files(backup_folder)
            backup.files_size_bytes = files_size
            backup.file_count = file_count
            
            # Write metadata
            self.stdout.write('Writing metadata...')
            self._write_metadata(backup_folder, backup)
            
            # Mark as successful
            backup.status = 'success'
            backup.end_time = timezone.now()
            success = True
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Backup completed: {backup_id}')
            )
            self.stdout.write(f'  Database: {db_size / (1024*1024):.2f} MB')
            self.stdout.write(f'  Files: {files_size / (1024*1024):.2f} MB ({file_count} files)')
            
        except Exception as e:
            error_message = str(e)
            backup.status = 'failed'
            backup.failure_reason = error_message
            backup.end_time = timezone.now()
            
            self.stdout.write(
                self.style.ERROR(f'✗ Backup failed: {error_message}')
            )
        
        finally:
            # Save backup record
            backup.save()
            
            # Log operation
            BackupLog.objects.create(
                backup=backup,
                operation='backup',
                status='success' if success else 'error',
                message=error_message or f'Backup created: {backup_id}',
                initiated_by='system',
                duration_seconds=(timezone.now() - start_time).total_seconds(),
                created_by=system_user,
                updated_by=system_user,
            )
            
            # Clean up old backups if requested
            if success and not options['no_cleanup']:
                self.stdout.write('Cleaning up old backups...')
                self._cleanup_old_backups(backup_root, settings_obj.retention_count)
    
    def _backup_database(self, backup_folder: Path) -> Tuple[Path, int]:
        """
        Create database dump using pg_dump and compress it.
        
        Returns:
            Tuple of (backup_file_path, size_in_bytes)
        """
        db_config = settings.DATABASES.get('default', {})
        
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3':
            # SQLite backup
            db_file = Path(db_config.get('NAME'))
            if not db_file.exists():
                raise CommandError(f"Database file not found: {db_file}")
            
            # Copy SQLite file
            output_file = backup_folder / 'database.db'
            shutil.copy2(db_file, output_file)
            size = output_file.stat().st_size
            
            # Compress
            gz_file = backup_folder / 'database.db.gz'
            with open(output_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            output_file.unlink()
            return gz_file, gz_file.stat().st_size
        
        elif db_config.get('ENGINE') == 'django.db.backends.postgresql':
            # PostgreSQL backup
            db_name = db_config.get('NAME', 'brixacore')
            db_user = db_config.get('USER', 'postgres')
            db_host = db_config.get('HOST', 'localhost')
            db_port = db_config.get('PORT', '5432')
            
            # Create uncompressed dump
            dump_file = backup_folder / 'database.sql'
            
            try:
                env = os.environ.copy()
                
                # Add common Postgres bin paths to PATH
                common_paths = [
                    '/Library/PostgreSQL/18/bin',
                    '/Library/PostgreSQL/17/bin',
                    '/Library/PostgreSQL/16/bin',
                    '/Applications/Postgres.app/Contents/Versions/latest/bin',
                    '/opt/homebrew/bin',
                    '/usr/local/bin',
                ]
                current_path = env.get('PATH', '')
                for p in common_paths:
                    if os.path.exists(p):
                        current_path = f"{p}:{current_path}"
                env['PATH'] = current_path

                if 'PASSWORD' in db_config:
                    # Create pgpass file for password authentication
                    pgpass_content = f"{db_host}:{db_port}:{db_name}:{db_user}:{db_config['PASSWORD']}\n"
                    env['PGPASSWORD'] = db_config['PASSWORD']
                
                cmd = [
                    'pg_dump',
                    '-h', db_host,
                    '-p', str(db_port),
                    '-U', db_user,
                    '-F', 'plain',  # Text format
                    db_name
                ]
                
                with open(dump_file, 'w') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        check=True,
                        text=True,
                    )
                
            except subprocess.CalledProcessError as e:
                raise CommandError(f"pg_dump failed: {e.stderr}")
            except FileNotFoundError:
                raise CommandError("pg_dump not found. Ensure PostgreSQL tools are installed.")
            
            # Compress dump
            gz_file = backup_folder / 'database.sql.gz'
            with open(dump_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            dump_file.unlink()
            return gz_file, gz_file.stat().st_size
        
        else:
            raise CommandError(f"Unsupported database backend: {db_config.get('ENGINE')}")
    
    def _backup_files(self, backup_folder: Path) -> Tuple[Path, int, int]:
        """
        Create tar.gz archive of file storage.
        
        Returns:
            Tuple of (archive_path, size_in_bytes, file_count)
        """
        storage_root = Path(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else None
        
        if not storage_root or not storage_root.exists():
            # No files to backup
            empty_tar = backup_folder / 'files.tar.gz'
            with tarfile.open(empty_tar, 'w:gz') as tar:
                pass  # Empty archive
            return empty_tar, 0, 0
        
        archive_path = backup_folder / 'files.tar.gz'
        file_count = 0
        
        try:
            with tarfile.open(archive_path, 'w:gz') as tar:
                for file_path in storage_root.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(storage_root)
                        tar.add(file_path, arcname=arcname)
                        file_count += 1
        except Exception as e:
            raise CommandError(f"Failed to create file archive: {str(e)}")
        
        size = archive_path.stat().st_size
        return archive_path, size, file_count
    
    def _write_metadata(self, backup_folder: Path, backup: Backup):
        """Write backup metadata as JSON."""
        metadata = {
            'backup_id': backup.backup_id,
            'timestamp': backup.backup_timestamp.isoformat(),
            'app_version': backup.app_version,
            'schema_version': backup.schema_version,
            'database_version': backup.database_version,
            'install_mode': backup.install_mode,
            'database_file': 'database.sql.gz' if backup.database_size_bytes else None,
            'files_archive': 'files.tar.gz' if backup.files_size_bytes else None,
            'file_count': backup.file_count,
        }
        
        metadata_file = backup_folder / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _cleanup_old_backups(self, backup_root: Path, retention_count: int):
        """Remove old backups beyond retention count."""
        if retention_count < 5:
            retention_count = 5
        
        try:
            # Get all backup folders, sorted by modification time
            backup_folders = sorted(
                [d for d in backup_root.iterdir() if d.is_dir() and d.name.startswith('backup_')],
                key=lambda d: d.stat().st_mtime,
                reverse=True
            )
            
            # Remove backups beyond retention
            for old_backup in backup_folders[retention_count:]:
                self.stdout.write(f'  Removing old backup: {old_backup.name}')
                shutil.rmtree(old_backup)
                
                # Delete associated Backup record
                try:
                    Backup.objects.filter(backup_id=old_backup.name).delete()
                except Exception:
                    pass
        
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Failed to clean up old backups: {str(e)}')
            )
    
    def _get_app_version(self) -> str:
        """Get BrixaWares application version."""
        # Try to read from version file or git
        try:
            version_file = Path(settings.BASE_DIR) / '.version'
            if version_file.exists():
                return version_file.read_text().strip()
        except Exception:
            pass
        
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                cwd=settings.BASE_DIR,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return '1.0.0'
    
    def _get_schema_version(self) -> str:
        """Get database schema version from Django."""
        from django.db.migrations.loader import MigrationLoader
        from django.apps import apps
        
        try:
            loader = MigrationLoader(None, ignores=['django.contrib.*'])
            # Get the latest migration
            graph = loader.graph
            leaf_nodes = graph.leaf_nodes()
            if leaf_nodes:
                last_migration = max(leaf_nodes, key=lambda x: x[1])
                return last_migration[1]
        except Exception:
            pass
        
        return '1.0.0'
    
    def _get_database_version(self) -> str:
        """Get database version."""
        db_config = settings.DATABASES.get('default', {})
        
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3':
            import sqlite3
            return f"SQLite {sqlite3.sqlite_version}"
        
        elif db_config.get('ENGINE') == 'django.db.backends.postgresql':
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute('SELECT version();')
                    version_str = cursor.fetchone()[0]
                    # Extract version number
                    import re
                    match = re.search(r'PostgreSQL (\d+\.\d+)', version_str)
                    if match:
                        return f"PostgreSQL {match.group(1)}"
                    return version_str.split(',')[0]
            except Exception:
                pass
        
        return 'Unknown'
