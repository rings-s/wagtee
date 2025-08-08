from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from utils.notification_manager import NotificationScheduler
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send scheduled notifications (reminders, summaries, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['reminders', 'summaries', 'subscriptions', 'all'],
            default='all',
            help='Type of notifications to send'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No notifications will be sent')
            )
        
        start_time = timezone.now()
        total_sent = 0
        
        try:
            if notification_type in ['reminders', 'all']:
                self.stdout.write('Processing booking reminders...')
                if not dry_run:
                    sent = NotificationScheduler.send_daily_reminders()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} reminder notifications')
                    )
                else:
                    from utils.notification_manager import NotificationManager
                    pending = NotificationManager.get_pending_reminders()
                    self.stdout.write(f'Would send {len(pending)} reminder notifications')
            
            if notification_type in ['summaries', 'all']:
                self.stdout.write('Processing daily summaries...')
                if not dry_run:
                    sent = NotificationScheduler.send_daily_summaries()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} daily summaries')
                    )
                else:
                    from utils.notification_manager import NotificationManager
                    businesses = NotificationManager.get_businesses_for_daily_summary()
                    self.stdout.write(f'Would send {len(businesses)} daily summaries')
            
            if notification_type in ['subscriptions', 'all']:
                self.stdout.write('Processing subscription reminders...')
                if not dry_run:
                    sent = NotificationScheduler.check_subscription_expiries()
                    total_sent += sent
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent {sent} subscription reminders')
                    )
                else:
                    self.stdout.write('Would check subscription expiries')
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully sent {total_sent} notifications in {duration:.2f} seconds'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Dry run completed in {duration:.2f} seconds')
                )
                
        except Exception as e:
            logger.error(f'Notification command failed: {str(e)}')
            raise CommandError(f'Failed to send notifications: {str(e)}')