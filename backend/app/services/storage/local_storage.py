"""
Local file system storage service for file uploads and downloads.
"""

import asyncio
import os
import shutil
from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime
import hashlib
import uuid

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class LocalStorageService:
    """
    Service for local file system storage operations.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or settings.LOCAL_STORAGE_PATH or "/tmp/cqia_storage"
        self._ensure_base_path()

    def _ensure_base_path(self) -> None:
        """
        Ensure the base storage path exists.
        """
        try:
            os.makedirs(self.base_path, exist_ok=True)
            logger.info(f"Ensured local storage path: {self.base_path}")
        except Exception as e:
            logger.error(f"Failed to create base storage path: {e}")
            raise

    def _get_file_path(self, file_key: str) -> str:
        """
        Get the full file path for a given key.
        """
        return os.path.join(self.base_path, file_key)

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.
        """
        # Remove path separators and other dangerous characters
        sanitized = "".join(c for c in filename if c.isalnum() or c in "._-")
        return sanitized

    async def upload_file(
        self,
        file_data: BinaryIO,
        file_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to local storage.
        """
        try:
            # Sanitize file key
            safe_file_key = self._sanitize_filename(file_key)

            # Create directory structure if needed
            file_path = self._get_file_path(safe_file_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write file
            with open(file_path, 'wb') as f:
                if hasattr(file_data, 'read'):
                    # If file_data is a file-like object
                    shutil.copyfileobj(file_data, f)
                    size = f.tell()
                else:
                    # If file_data is bytes
                    f.write(file_data)
                    size = len(file_data)

            # Generate file hash
            file_hash = await self._calculate_file_hash(file_path)

            # Save metadata
            metadata_file = f"{file_path}.meta"
            if metadata:
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f)

            return {
                'success': True,
                'file_key': safe_file_key,
                'file_path': file_path,
                'size': size,
                'hash': file_hash,
                'content_type': content_type,
                'uploaded_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }

        except Exception as e:
            logger.error(f"Local file upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def download_file(self, file_key: str) -> Dict[str, Any]:
        """
        Download a file from local storage.
        """
        try:
            file_path = self._get_file_path(file_key)

            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_key': file_key
                }

            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Get file stats
            stat = os.stat(file_path)

            # Read metadata if exists
            metadata = {}
            metadata_file = f"{file_path}.meta"
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except Exception:
                    pass  # Ignore metadata read errors

            return {
                'success': True,
                'file_key': file_key,
                'file_path': file_path,
                'body': file_data,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Local file download failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def delete_file(self, file_key: str) -> Dict[str, Any]:
        """
        Delete a file from local storage.
        """
        try:
            file_path = self._get_file_path(file_key)

            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_key': file_key
                }

            # Delete file
            os.remove(file_path)

            # Delete metadata file if exists
            metadata_file = f"{file_path}.meta"
            if os.path.exists(metadata_file):
                os.remove(metadata_file)

            return {
                'success': True,
                'file_key': file_key,
                'deleted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Local file deletion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def list_files(
        self,
        prefix: Optional[str] = None,
        max_files: int = 100
    ) -> Dict[str, Any]:
        """
        List files in local storage.
        """
        try:
            files = []

            # Walk through directory
            for root, dirs, filenames in os.walk(self.base_path):
                for filename in filenames:
                    # Skip metadata files
                    if filename.endswith('.meta'):
                        continue

                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.base_path)

                    # Apply prefix filter
                    if prefix and not rel_path.startswith(prefix):
                        continue

                    # Get file stats
                    stat = os.stat(file_path)

                    # Read metadata if exists
                    metadata = {}
                    metadata_file = f"{file_path}.meta"
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                        except Exception:
                            pass

                    files.append({
                        'key': rel_path,
                        'file_path': file_path,
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'metadata': metadata
                    })

                    # Limit results
                    if len(files) >= max_files:
                        break

            # Sort by last modified (newest first)
            files.sort(key=lambda x: x['last_modified'], reverse=True)

            return {
                'success': True,
                'files': files,
                'total_count': len(files),
                'base_path': self.base_path
            }

        except Exception as e:
            logger.error(f"Local file listing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

    async def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        """
        Get file metadata from local storage.
        """
        try:
            file_path = self._get_file_path(file_key)

            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_key': file_key
                }

            # Get file stats
            stat = os.stat(file_path)

            # Read metadata if exists
            metadata = {}
            metadata_file = f"{file_path}.meta"
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except Exception:
                    pass

            return {
                'success': True,
                'file_key': file_key,
                'file_path': file_path,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'metadata': metadata,
                'exists': True
            }

        except Exception as e:
            logger.error(f"Local metadata fetch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def copy_file(
        self,
        source_key: str,
        destination_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Copy a file within local storage.
        """
        try:
            source_path = self._get_file_path(source_key)
            dest_path = self._get_file_path(destination_key)

            if not os.path.exists(source_path):
                return {
                    'success': False,
                    'error': 'Source file not found',
                    'source_key': source_key,
                    'destination_key': destination_key
                }

            # Create destination directory
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copy file
            shutil.copy2(source_path, dest_path)

            # Copy metadata if exists
            source_metadata_file = f"{source_path}.meta"
            dest_metadata_file = f"{dest_path}.meta"
            if os.path.exists(source_metadata_file):
                shutil.copy2(source_metadata_file, dest_metadata_file)

            # Update metadata if provided
            if metadata:
                with open(dest_metadata_file, 'w') as f:
                    json.dump(metadata, f)

            return {
                'success': True,
                'source_key': source_key,
                'destination_key': destination_key,
                'source_path': source_path,
                'destination_path': dest_path,
                'copied_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Local file copy failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_key': source_key,
                'destination_key': destination_key
            }

    async def move_file(
        self,
        source_key: str,
        destination_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Move a file within local storage.
        """
        try:
            source_path = self._get_file_path(source_key)
            dest_path = self._get_file_path(destination_key)

            if not os.path.exists(source_path):
                return {
                    'success': False,
                    'error': 'Source file not found',
                    'source_key': source_key,
                    'destination_key': destination_key
                }

            # Create destination directory
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Move file
            shutil.move(source_path, dest_path)

            # Move metadata file if exists
            source_metadata_file = f"{source_path}.meta"
            dest_metadata_file = f"{dest_path}.meta"
            if os.path.exists(source_metadata_file):
                shutil.move(source_metadata_file, dest_metadata_file)

            # Update metadata if provided
            if metadata:
                with open(dest_metadata_file, 'w') as f:
                    json.dump(metadata, f)

            return {
                'success': True,
                'source_key': source_key,
                'destination_key': destination_key,
                'source_path': source_path,
                'destination_path': dest_path,
                'moved_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Local file move failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_key': source_key,
                'destination_key': destination_key
            }

    async def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"File hash calculation failed: {e}")
            return ""

    async def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information and statistics.
        """
        try:
            # Get disk usage
            stat = shutil.disk_usage(self.base_path)

            # Count files and calculate total size
            total_files = 0
            total_size = 0

            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    if not file.endswith('.meta'):  # Exclude metadata files from count
                        total_files += 1
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                        except OSError:
                            pass  # Skip files that can't be accessed

            return {
                'success': True,
                'base_path': self.base_path,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'disk_free_bytes': stat.free,
                'disk_free_mb': round(stat.free / (1024 * 1024), 2),
                'disk_total_bytes': stat.total,
                'disk_total_mb': round(stat.total / (1024 * 1024), 2),
                'disk_used_bytes': stat.used,
                'disk_used_mb': round(stat.used / (1024 * 1024), 2),
                'usage_percentage': round((stat.used / stat.total) * 100, 2)
            }

        except Exception as e:
            logger.error(f"Storage info fetch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'base_path': self.base_path
            }

    async def cleanup_old_files(self, days_old: int = 30) -> Dict[str, Any]:
        """
        Clean up files older than specified days.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            deleted_files = []
            total_size_freed = 0

            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    if file.endswith('.meta'):
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        # Check file age
                        stat = os.stat(file_path)
                        file_modified = datetime.fromtimestamp(stat.st_mtime)

                        if file_modified < cutoff_date:
                            # Delete file
                            size = stat.st_size
                            os.remove(file_path)
                            total_size_freed += size
                            deleted_files.append(file_path)

                            # Delete metadata file if exists
                            metadata_file = f"{file_path}.meta"
                            if os.path.exists(metadata_file):
                                os.remove(metadata_file)

                    except OSError:
                        pass  # Skip files that can't be deleted

            return {
                'success': True,
                'deleted_files_count': len(deleted_files),
                'size_freed_bytes': total_size_freed,
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2),
                'cutoff_date': cutoff_date.isoformat(),
                'cleanup_completed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"File cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def check_health(self) -> bool:
        """
        Check if local storage service is healthy.
        """
        try:
            # Test basic operations
            test_key = f"health_check_{uuid.uuid4().hex}"
            test_data = b"test data"

            # Test upload
            upload_result = await self.upload_file(test_data, test_key)
            if not upload_result['success']:
                return False

            # Test download
            download_result = await self.download_file(test_key)
            if not download_result['success']:
                return False

            # Test delete
            delete_result = await self.delete_file(test_key)
            if not delete_result['success']:
                return False

            return True

        except Exception:
            return False
