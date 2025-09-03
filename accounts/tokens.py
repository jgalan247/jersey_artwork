# accounts/tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generator for email verification links.
    Inherits from PasswordResetTokenGenerator for security.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Create a hash value including user's email verification status.
        Token becomes invalid once email is verified.
        """
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.email_verified)
        )

# Create a single instance to use throughout the app
email_verification_token = EmailVerificationTokenGenerator()