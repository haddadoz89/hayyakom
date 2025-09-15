from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app.models import Funding, Notification

class Command(BaseCommand):
    help = 'Updates the status of campaigns that have passed their end date.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        expired_campaigns = Funding.objects.filter(status='In Process', end_date__lt=today)
        
        self.stdout.write(f'Found {expired_campaigns.count()} expired campaigns to process...')

        completed_count = 0
        failed_count = 0

        for campaign in expired_campaigns:
            if campaign.total_invested() >= campaign.goal:
                campaign.status = 'Completed'
                completed_count += 1
                
                investments = campaign.investment_set.all()
                for investment in investments:
                    investment.status = 'Collected'
                    investment.save()
                    Notification.objects.create(
                        user=investment.investor,
                        message=f"Good news! The campaign '{campaign.campaign_name}' was successful. Your investment of {investment.amount} BD has been collected.",
                        related_funding=campaign
                    )

            else:
                campaign.status = 'Failed'
                failed_count += 1
                
                investments_to_return = campaign.investment_set.filter(status='Pledged')
                for investment in investments_to_return:
                    investment.status = 'Returned'
                    investment.save()
                    
                    Notification.objects.create(
                        user=investment.investor,
                        message=f"The campaign '{campaign.campaign_name}' did not meet its goal. Your investment of {investment.amount} BD has been marked as returned.",
                        related_funding=campaign
                    )
            
            campaign.save()

        self.stdout.write(self.style.SUCCESS(
            f'Processing complete. Marked {completed_count} as Completed and {failed_count} as Failed.'
        ))