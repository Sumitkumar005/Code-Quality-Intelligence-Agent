"""
File storage service for managing file operations.
"""

import os
import shutil
import json
from typing import Dict, List, Any, Optional, BinaryIO
from pathlib import Path
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class FileStorage:
    """
    Service for file storage operations.
    """

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.STORAGE_PATH or "storage")
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        directory: str = ""
    ) -> Dict[str, Any]:
        """
        Save a file to storage.
        """
        try:
            # Create directory if it doesn't exist
            file_path = self.base_path / directory / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'directory': directory,
                'size': len(file_content)
            }

        except Exception as e:
            logger.error(f"File save failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }

    async def save_text_file(
        self,
        content: str,
        filename: str,
        directory: str = ""
    ) -> Dict[str, Any]:
        """
        Save text content to a file.
        """
        try:
            file_path = self.base_path / directory / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'directory': directory,
                'size': len(content.encode('utf-8'))
            }

        except Exception as e:
            logger.error(f"Text file save failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }

    async def save_json_file(
        self,
        data: Dict[str, Any],
        filename: str,
        directory: str = ""
    ) -> Dict[str, Any]:
        """
        Save data as JSON file.
        """
        try:
            json_content = json.dumps(data, indent=2, default=str)
            return await self.save_text_file(json_content, filename, directory)

        except Exception as e:
            logger.error(f"JSON file save failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file from storage.
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_path': file_path
                }

            with open(full_path, 'rb') as f:
                content = f.read()

            return {
                'success': True,
                'content': content,
                'file_path': str(full_path),
                'size': len(content)
            }

        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def read_text_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a text file from storage.
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_path': file_path
                }

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'success': True,
                'content': content,
                'file_path': str(full_path),
                'size': len(content.encode('utf-8'))
            }

        except Exception as e:
            logger.error(f"Text file read failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a JSON file from storage.
        """
        try:
            text_result = await self.read_text_file(file_path)
            if not text_result['success']:
                return text_result

            data = json.loads(text_result['content'])

            return {
                'success': True,
                'data': data,
                'file_path': text_result['file_path'],
                'size': text_result['size']
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed: {e}")
            return {
                'success': False,
                'error': f'Invalid JSON: {e}',
                'file_path': file_path
            }
        except Exception as e:
            logger.error(f"JSON file read failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file from storage.
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_path': file_path
                }

            full_path.unlink()

            return {
                'success': True,
                'file_path': str(full_path)
            }

        except Exception as e:
            logger.error(f"File delete failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def list_files(self, directory: str = "") -> Dict[str, Any]:
        """
        List files in a directory.
        """
        try:
            dir_path = self.base_path / directory

            if not dir_path.exists():
                return {
                    'success': False,
                    'error': 'Directory not found',
                    'directory': directory
                }

            files = []
            for item in dir_path.rglob('*'):
                if item.is_file():
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'path': str(item.relative_to(self.base_path)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

            return {
                'success': True,
                'files': files,
                'directory': directory,
                'count': len(files)
            }

        except Exception as e:
            logger.error(f"File listing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory': directory
            }

    async def create_directory(self, directory: str) -> Dict[str, Any]:
        """
        Create a directory.
        """
        try:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            return {
                'success': True,
                'directory': str(dir_path)
            }

        except Exception as e:
            logger.error(f"Directory creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory': directory
            }

    async def copy_file(
        self,
        source_path: str,
        destination_path: str
    ) -> Dict[str, Any]:
        """
        Copy a file within storage.
        """
        try:
            src = self.base_path / source_path
            dst = self.base_path / destination_path

            if not src.exists():
                return {
                    'success': False,
                    'error': 'Source file not found',
                    'source': source_path
                }

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

            return {
                'success': True,
                'source': str(src),
                'destination': str(dst)
            }

        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': source_path,
                'destination': destination_path
            }

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'file_path': file_path
                }

            stat = full_path.stat()

            return {
                'success': True,
                'file_path': str(full_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True
            }

        except Exception as e:
            logger.error(f"File info retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }

    async def check_health(self) -> bool:
        """
        Check if storage is accessible.
        """
        try:
            # Try to create and delete a test file
            test_file = self.base_path / ".health_check"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
