from django.core.management.base import BaseCommand
from django.db import connection, transaction
from hive_sbi_api.steem.domain.elt import run_incremental_elt

class Command(BaseCommand):
    help = 'Runs the incremental ELT pipeline for Steem operations'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting incremental Steem ELT pipeline...'))
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    run_incremental_elt(cursor)
            self.stdout.write(self.style.SUCCESS('Successfully completed incremental Steem ELT pipeline'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to execute Steem ELT pipeline: {str(e)}'))
            raise
