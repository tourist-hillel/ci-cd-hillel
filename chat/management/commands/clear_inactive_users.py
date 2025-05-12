from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Deletes inactive users for a specific timedelta'


    def add_arguments(self, parser):
       parser.add_argument(
           '--days',
           type=int,
           default=90,
           help='Number of days since last user login'
       )
       parser.add_argument(
           '--no_login_attempt',
           type=bool,
           default=False,
           help='Number of days since last user login'
       )

    def handle(self, *args, **options):
        days = options['days']
        no_login_attempt = options['no_login_attempt']
        last_login_date = timezone.now() - timedelta(days=days)
        logger.info('Start processing clean command')
        if no_login_attempt:
            self.stdout.write(
                self.style.WARNING(f'Users with no login attempt selected for deleting ...')
            )
            inactive_users = User.objects.filter(
                last_login__isnull=True,
            )
        else: 
            inactive_users = User.objects.filter(
                last_login__lt=last_login_date,
                is_staff=False,
                is_superuser=False
            )

        inactive_count = inactive_users.count()
        logger.info(f'Found {inactive_count} inactive users...')
        if inactive_count > 0:
            message = f'This list of users successfuly deleted: {inactive_users}'
            inactive_users.delete()
            logger.info(message)
            self.stdout.write(
                self.style.SUCCESS(message)
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'No inactive users found...')
            )