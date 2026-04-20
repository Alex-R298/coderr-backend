from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from profiles_app.models import UserProfile


GUEST_USERS = [
    {
        'username': 'customer',
        'password': '123456',
        'email': 'customer@guest.de',
        'type': 'customer',
    },
    {
        'username': 'business',
        'password': '123456',
        'email': 'business@guest.de',
        'type': 'business',
    },
]


class Command(BaseCommand):
    """Creates guest user accounts for testing and demo purposes."""

    help = 'Creates guest customer and business users with auth tokens.'

    def handle(self, *args, **options):
        for guest in GUEST_USERS:
            user, created = User.objects.get_or_create(
                username=guest['username'],
                defaults={'email': guest['email']},
            )
            if created:
                user.set_password(guest['password'])
                user.save()
                Token.objects.create(user=user)
                UserProfile.objects.create(user=user, type=guest['type'])
                self.stdout.write(self.style.SUCCESS(
                    f"Guest user '{guest['username']}' created."
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"Guest user '{guest['username']}' already exists."
                ))
