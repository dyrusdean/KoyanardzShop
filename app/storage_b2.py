"""
Custom storage backend for Backblaze B2 cloud storage.
Used for storing 3D model files.
"""
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import File
from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os
import io
import logging

logger = logging.getLogger(__name__)


class B2Storage(Storage):
    """
    Backblaze B2 storage backend for Django.
    Handles uploading and retrieving files from B2.
    """
    
    def __init__(self):
        """Initialize B2 connection with credentials from settings."""
        try:
            self.account_info = InMemoryAccountInfo()
            self.api = B2Api(self.account_info)
            
            # Get B2 credentials from Django settings
            self.application_key_id = getattr(settings, 'B2_APPLICATION_KEY_ID', '')
            self.application_key = getattr(settings, 'B2_APPLICATION_KEY', '')
            self.bucket_name = getattr(settings, 'B2_BUCKET_NAME', '')
            self.bucket_id = getattr(settings, 'B2_BUCKET_ID', '')
            self.endpoint = getattr(settings, 'B2_ENDPOINT', '')
            
            if not all([self.application_key_id, self.application_key, self.bucket_id]):
                raise ValueError("Missing B2 credentials in settings")
            
            # Authorize B2 API
            logger.info("Authorizing B2 API...")
            self.api.authorize_account('production', self.application_key_id, self.application_key)
            self.bucket = self.api.get_bucket_by_id(self.bucket_id)
            logger.info(f"✓ B2 connection established. Bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize B2Storage: {e}")
            raise
    
    def _open(self, name, mode='rb'):
        """
        Open and return the file from B2.
        """
        try:
            file_version = self.bucket.get_file_info_by_name(name)
            response = self.bucket.download_file_by_id(file_version.id_)
            return File(io.BytesIO(response.read()), name)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in B2: {str(e)}")
    
    def _save(self, name, content):
        """
        Save the file to B2.
        """
        try:
            # Normalize path separators - B2 requires forward slashes
            name = name.replace('\\', '/')
            
            # Read the content
            if hasattr(content, 'read'):
                file_data = content.read()
            else:
                file_data = content
            
            # Upload to B2
            logger.info(f"Uploading to B2: {name} ({len(file_data)} bytes)")
            file_version = self.bucket.upload_bytes(
                file_data,
                file_name=name,
                file_info={}
            )
            
            logger.info(f"✓ Successfully uploaded to B2: {name}")
            return file_version.file_name
        except Exception as e:
            logger.error(f"✗ Error uploading file to B2: {str(e)}")
            raise Exception(f"Error uploading file to B2: {str(e)}")
    
    def delete(self, name):
        """
        Delete the file from B2.
        """
        try:
            file_version = self.bucket.get_file_info_by_name(name)
            self.bucket.delete_file_version(file_version.id_, name)
        except Exception as e:
            raise Exception(f"Error deleting file from B2: {str(e)}")
    
    def exists(self, name):
        """
        Check if the file exists in B2.
        """
        try:
            self.bucket.get_file_info_by_name(name)
            return True
        except:
            return False
    
    def listdir(self, path):
        """
        List files in B2 bucket at the given path.
        """
        try:
            directories = []
            files = []
            
            for file_version, _ in self.bucket.ls(
                recursive=False,
                fetch_count=100,
                start_filename=path
            ):
                if file_version is not None:
                    files.append(file_version.file_name)
            
            return directories, files
        except Exception as e:
            raise Exception(f"Error listing B2 bucket: {str(e)}")
    
    def size(self, name):
        """
        Return the total size, in bytes, of the file.
        """
        try:
            file_version = self.bucket.get_file_info_by_name(name)
            return file_version.size
        except Exception as e:
            raise Exception(f"Error getting file size from B2: {str(e)}")
    
    def url(self, name):
        """
        Return the full URL where the file can be accessed.
        """
        # B2 URL format: https://{endpoint}/{bucket_name}/{file_name}
        return f"https://{self.endpoint}/{self.bucket_name}/{name}"
    
    def get_accessed_time(self, name):
        """
        Return the last accessed time.
        """
        raise NotImplementedError("B2 storage does not support accessed time.")
    
    def get_created_time(self, name):
        """
        Return the creation time.
        """
        raise NotImplementedError("B2 storage does not support created time.")
    
    def get_modified_time(self, name):
        """
        Return the last modified time.
        """
        raise NotImplementedError("B2 storage does not support modified time.")
