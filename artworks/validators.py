"""
File upload validators and security utilities for the Jersey Artwork platform.
"""
import os
import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import hashlib
import uuid


class FileValidator:
    """Comprehensive file validation for secure uploads."""

    # Maximum file size: 5MB for images
    MAX_FILE_SIZE = 5 * 1024 * 1024

    # Allowed MIME types and extensions
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/webp': ['.webp'],
    }

    # Malicious patterns to check
    MALICIOUS_PATTERNS = [
        b'<?php',
        b'<script',
        b'javascript:',
        b'<iframe',
        b'<embed',
        b'<object',
    ]

    @classmethod
    def validate_image_upload(cls, file):
        """
        Comprehensive image file validation.

        Args:
            file: Django UploadedFile object

        Raises:
            ValidationError: If file fails validation
        """
        # Check file size
        if file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                _('File size exceeds maximum allowed size of 5MB.'),
                code='file_too_large'
            )

        # Check file extension
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = []
        for extensions in cls.ALLOWED_IMAGE_TYPES.values():
            valid_extensions.extend(extensions)

        if ext not in valid_extensions:
            raise ValidationError(
                _('Invalid file extension. Allowed: %(extensions)s'),
                params={'extensions': ', '.join(valid_extensions)},
                code='invalid_extension'
            )

        # Check MIME type using python-magic
        file.seek(0)
        file_mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)

        if file_mime not in cls.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                _('Invalid file type. Only JPEG, PNG, and WebP images are allowed.'),
                code='invalid_mime_type'
            )

        # Verify it's a valid image using PIL
        try:
            file.seek(0)
            img = Image.open(file)
            img.verify()
            file.seek(0)
        except Exception:
            raise ValidationError(
                _('Invalid or corrupted image file.'),
                code='invalid_image'
            )

        # Check for malicious content
        file.seek(0)
        file_content = file.read()
        file.seek(0)

        for pattern in cls.MALICIOUS_PATTERNS:
            if pattern in file_content:
                raise ValidationError(
                    _('File contains potentially malicious content.'),
                    code='malicious_content'
                )

        # Check image dimensions
        file.seek(0)
        img = Image.open(file)
        width, height = img.size
        file.seek(0)

        # Maximum dimensions: 4000x4000
        if width > 4000 or height > 4000:
            raise ValidationError(
                _('Image dimensions exceed maximum allowed (4000x4000).'),
                code='dimensions_too_large'
            )

        # Minimum dimensions: 100x100
        if width < 100 or height < 100:
            raise ValidationError(
                _('Image dimensions too small. Minimum: 100x100 pixels.'),
                code='dimensions_too_small'
            )

        return True


def generate_secure_filename(original_filename):
    """
    Generate a secure filename with UUID to prevent collisions and path traversal.

    Args:
        original_filename: Original uploaded filename

    Returns:
        Secure filename with UUID prefix
    """
    ext = os.path.splitext(original_filename)[1].lower()
    # Generate UUID-based filename
    unique_id = uuid.uuid4().hex[:8]
    timestamp = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]
    secure_name = f"{unique_id}_{timestamp}{ext}"
    return secure_name


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove potentially dangerous characters
    dangerous_chars = ['/', '\\', '..', '~', '$', '`', '|', '<', '>', ';', '&']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]

    return f"{name}{ext}"


class ContentTypeValidator:
    """Validate content types for various file uploads."""

    DOCUMENT_TYPES = {
        'application/pdf': ['.pdf'],
    }

    @classmethod
    def validate_document(cls, file):
        """Validate document uploads (e.g., invoices, reports)."""
        if file.size > 10 * 1024 * 1024:  # 10MB max for documents
            raise ValidationError(_('Document size exceeds 10MB limit.'))

        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = []
        for extensions in cls.DOCUMENT_TYPES.values():
            valid_extensions.extend(extensions)

        if ext not in valid_extensions:
            raise ValidationError(
                _('Invalid document type. Only PDF files are allowed.')
            )

        # Check MIME type
        file.seek(0)
        file_mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)

        if file_mime not in cls.DOCUMENT_TYPES:
            raise ValidationError(_('Invalid document MIME type.'))

        return True