import pandas as pd
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Populate the database with users"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='Path to the CSV file')

    def handle(self, *args, **options):

        ans = input("Do you want to delete all previous users? (y/n): ")
        if ans == 'y':
            User.objects.all().delete()
            print("Deleted all users")
        
        csv_file = options['csv_file']
        df = pd.read_csv(csv_file)
        df = df.where(pd.notnull(df), None) #this converts NaN to None
        for index, row in df.iterrows():
            try:
                user = User.objects.create_user(
                    email=row['email'],
                    full_name=row['full_name'],
                    phone_number=row['phone_number'],
                    password=str(row['password']),
                    is_ticc_counsellor=row['is_ticc_counsellor'],
                    is_ticc_manager=row['is_ticc_manager'],
                )
                user.save()
                print(f"Created user {user.email}")
            except Exception as e:
                print(f"Error creating user {row['email']}: {e}")

        print("Done populating users")

