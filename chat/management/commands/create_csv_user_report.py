import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime  import datetime

class Command(BaseCommand):
    help= 'SCV Report'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'user_report_{timestamp}.csv'

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Username', 'Email', 'First name', 'Last name', 'Date joined', 'Last login'])

            for user in User.objects.all():
                writer.writerow([
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.date_joined,
                    user.last_login
                ])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfuly created report {filename}'
            )
        )