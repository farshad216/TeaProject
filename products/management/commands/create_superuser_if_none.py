"""
Management command to create a superuser if none exists.
This is useful for deployment platforms without shell access.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist. Uses environment variables for credentials.'

    def handle(self, *args, **options):
        # Get credentials from environment variables
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_PASSWORD not set. Cannot create superuser automatically.\n'
                    'Please set DJANGO_SUPERUSER_PASSWORD environment variable in Render dashboard.'
                )
            )
            return

        # Check if a superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists. Skipping creation.'))
            return

        # Check if a user with this username already exists
        try:
            existing_user = User.objects.get(username=username)
            # If user exists but is not a superuser, upgrade them
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                existing_user.is_staff = True
                existing_user.set_password(password)
                if email:
                    existing_user.email = email
                existing_user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully upgraded existing user to superuser: {username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'User {username} already exists and is a superuser.'
                    )
                )
            return
        except User.DoesNotExist:
            # User doesn't exist, create new one
            pass

        # Create new superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # Explicitly ensure is_staff is True (should be automatic, but being safe)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created superuser: {username} (is_staff={user.is_staff}, is_superuser={user.is_superuser})'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

