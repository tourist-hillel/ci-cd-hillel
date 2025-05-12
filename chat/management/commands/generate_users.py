from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Generates fake users'


    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of fake users'
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        created_count = 0

        for _ in range(count):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name() + str(random.randint(1, 999))
            
            email = fake.email()
            while User.objects.filter(email=email).exists():
                username = fake.email()

            # hardcoded_pwd = 'SuperPuperPWD123'
            user = User.objects.create_user(
                username=username,
                email=email,
                password = fake.password(),
                first_name = fake.first_name(),
                last_name = fake.last_name(),
            )

            user.is_active = random.choice([True, False])
            user.save()
            self.stdout.write(
                self.style.NOTICE(
                    f'Created user {user.username}'
                )
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfuly created {created_count} fake users'
            )
        )
            
            

            

            