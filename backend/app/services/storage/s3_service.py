"""
AWS S3 storage service for file uploads and downloads.
"""

import asyncio
import boto3
from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime
import os

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class S3Service:
    """
    Service for AWS S3 file storage operations.
    """

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        bucket_name: Optional[str] = None
    ):
        self.aws_access_key_id = aws_access_key_id or settings.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key or settings.AWS_SECRET_ACCESS_KEY
        self.region_name = region_name or settings.AWS_REGION or "us-east-1"
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

        # Initialize S3 resource for higher-level operations
        self.s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    async def upload_file(
        self,
        file_data: BinaryIO,
        file_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to S3.
        """
        try:
            # Ensure bucket exists
            await self._ensure_bucket_exists()

            # Prepare upload parameters
            upload_args = {
                'Bucket': self.bucket_name,
                'Key': file_key,
                'Body': file_data
            }

            if content_type:
                upload_args['ContentType'] = content_type

            if metadata:
                upload_args['Metadata'] = metadata

            # Upload file
            response = self.s3_client.put_object(**upload_args)

            return {
                'success': True,
                'file_key': file_key,
                'bucket': self.bucket_name,
                'etag': response.get('ETag', ''),
                'version_id': response.get('VersionId'),
                'uploaded_at': datetime.utcnow().isoformat(),
                'size': len(file_data.read()) if hasattr(file_data, 'read') else 0
            }

        except Exception as e:
            logger.error(f"S3 file upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def download_file(self, file_key: str) -> Dict[str, Any]:
        """
        Download a file from S3.
        """
        try:
            # Download file
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)

            return {
                'success': True,
                'file_key': file_key,
                'body': response['Body'],
                'content_type': response.get('ContentType', ''),
                'content_length': response.get('ContentLength', 0),
                'etag': response.get('ETag', ''),
                'last_modified': response.get('LastModified', datetime.utcnow()).isoformat(),
                'metadata': response.get('Metadata', {})
            }

        except Exception as e:
            logger.error(f"S3 file download failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def delete_file(self, file_key: str) -> Dict[str, Any]:
        """
        Delete a file from S3.
        """
        try:
            # Delete file
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)

            return {
                'success': True,
                'file_key': file_key,
                'deleted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"S3 file deletion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def list_files(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 100
    ) -> Dict[str, Any]:
        """
        List files in S3 bucket.
        """
        try:
            # List objects
            list_args = {
                'Bucket': self.bucket_name,
                'MaxKeys': max_keys
            }

            if prefix:
                list_args['Prefix'] = prefix

            response = self.s3_client.list_objects_v2(**list_args)

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'],
                        'storage_class': obj.get('StorageClass', 'STANDARD')
                    })

            return {
                'success': True,
                'files': files,
                'key_count': response.get('KeyCount', 0),
                'is_truncated': response.get('IsTruncated', False),
                'next_continuation_token': response.get('NextContinuationToken')
            }

        except Exception as e:
            logger.error(f"S3 file listing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

    async def get_file_metadata(self, file_key: str) -> Dict[str, Any]:
        """
        Get file metadata from S3.
        """
        try:
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)

            return {
                'success': True,
                'file_key': file_key,
                'content_type': response.get('ContentType', ''),
                'content_length': response.get('ContentLength', 0),
                'etag': response.get('ETag', ''),
                'last_modified': response.get('LastModified', datetime.utcnow()).isoformat(),
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId'),
                'storage_class': response.get('StorageClass', 'STANDARD')
            }

        except Exception as e:
            logger.error(f"S3 metadata fetch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_key': file_key
            }

    async def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
        operation: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Generate a presigned URL for S3 operations.
        """
        try:
            if operation.upper() == 'GET':
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_key},
                    ExpiresIn=expiration
                )
            elif operation.upper() == 'PUT':
                url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_key},
                    ExpiresIn=expiration
                )
            else:
                return {
                    'success': False,
                    'error': f'Unsupported operation: {operation}',
                    'file_key': file_key
                }

            return {
                'success': True,
                'file_key': file_key,
                'presigned_url': url,
                'expiration': expiration,
                'operation': operation,
                'expires_at': (datetime.utcnow() + timedelta(seconds=expiration)).isoformat()
            }

        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}")
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
        Copy a file within S3.
        """
        try:
            copy_args = {
                'CopySource': {'Bucket': self.bucket_name, 'Key': source_key},
                'Bucket': self.bucket_name,
                'Key': destination_key
            }

            if metadata:
                copy_args['Metadata'] = metadata
                copy_args['MetadataDirective'] = 'REPLACE'

            response = self.s3_client.copy_object(**copy_args)

            return {
                'success': True,
                'source_key': source_key,
                'destination_key': destination_key,
                'copy_source_version_id': response.get('CopySourceVersionId'),
                'version_id': response.get('VersionId'),
                'copied_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"S3 file copy failed: {e}")
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
        Move a file within S3 (copy + delete).
        """
        try:
            # Copy file
            copy_result = await self.copy_file(source_key, destination_key, metadata)
            if not copy_result['success']:
                return copy_result

            # Delete source file
            delete_result = await self.delete_file(source_key)
            if not delete_result['success']:
                logger.warning(f"File moved but source deletion failed: {source_key}")

            return {
                'success': True,
                'source_key': source_key,
                'destination_key': destination_key,
                'moved_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"S3 file move failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_key': source_key,
                'destination_key': destination_key
            }

    async def _ensure_bucket_exists(self) -> bool:
        """
        Ensure the S3 bucket exists, create if it doesn't.
        """
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)

        except Exception:
            # Bucket doesn't exist, create it
            try:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region_name
                    } if self.region_name != 'us-east-1' else {}
                )
                logger.info(f"Created S3 bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to create S3 bucket: {e}")
                raise

        return True

    async def get_bucket_info(self) -> Dict[str, Any]:
        """
        Get bucket information and statistics.
        """
        try:
            # Get bucket location
            location_response = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            location = location_response.get('LocationConstraint', 'us-east-1')

            # Get bucket statistics (approximate)
            bucket_resource = self.s3_resource.Bucket(self.bucket_name)
            objects = list(bucket_resource.objects.all())

            total_size = sum(obj.size for obj in objects)
            object_count = len(objects)

            return {
                'success': True,
                'bucket_name': self.bucket_name,
                'region': location,
                'object_count': object_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'created_at': datetime.utcnow().isoformat()  # Approximate
            }

        except Exception as e:
            logger.error(f"Bucket info fetch failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'bucket_name': self.bucket_name
            }

    async def check_health(self) -> bool:
        """
        Check if S3 service is healthy.
        """
        try:
            # Test bucket access
            await self._ensure_bucket_exists()
            return True
        except Exception:
            return False
