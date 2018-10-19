'''

'''

from django.core.management.base import BaseCommand

from devsite import seed

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass


    def handle(self, *args, **options):
        print('Seeding mock data for Figures demo')
        seed.seed_course_overviews()

        seed.wipe()
        seed.seed_all()
        print('Done.')
