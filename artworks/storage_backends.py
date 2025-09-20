"""
Custom storage backends for Digital Ocean Spaces.
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files."""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True
    custom_domain = False


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files with security considerations."""
    location = 'media'
    default_acl = 'private'  # Private by default for user uploads
    file_overwrite = False  # Don't overwrite existing files
    custom_domain = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom parameters for different file types
        self.object_parameters = {
            'CacheControl': 'max-age=86400',
        }

    def get_object_parameters(self, name):
        """
        Set specific parameters based on file type.
        """
        params = super().get_object_parameters(name)

        # Set content disposition for downloads
        if name.endswith('.pdf'):
            params['ContentDisposition'] = 'attachment'

        # Set cache control for images
        if any(name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            params['CacheControl'] = 'max-age=31536000'  # 1 year for images

        return params


class SecureMediaStorage(S3Boto3Storage):
    """
    Secure storage for sensitive documents.
    Files are private and require signed URLs for access.
    """
    location = 'secure'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    querystring_auth = True  # Always use signed URLs
    querystring_expire = 3600  # URLs expire after 1 hour

    def get_object_parameters(self, name):
        """Force download for all secure files."""
        params = super().get_object_parameters(name)
        params['ContentDisposition'] = 'attachment'
        params['ServerSideEncryption'] = 'AES256'  # Encrypt at rest
        return params