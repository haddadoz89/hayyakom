from datetime import timedelta, timezone
from django.contrib import admin
from .models import Profile, Company, Funding, Investment, Notification, Milestone

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone_number')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'owner', 'cr_number')
    search_fields = ('company_name', 'owner__username')

@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    list_filter = ('is_approved', 'status', 'category')
    list_display = ('campaign_name', 'company', 'status', 'is_approved', 'goal', 'reveal_date')
    search_fields = ('campaign_name', 'company__company_name')
    actions = ['approve_campaigns', 'add_to_next_pulse']

    def approve_campaigns(self, request, queryset):
        for campaign in queryset:
            campaign.is_approved = True
            campaign.status = 'Pending Pulse'
            campaign.save()
            Notification.objects.create(
                user=campaign.company.owner,
                message=f"Congratulations! Your campaign '{campaign.campaign_name}' has been approved.",
                related_funding=campaign
            )
    
    approve_campaigns.short_description = "Approve selected campaigns"

    def add_to_next_pulse(self, request, queryset):
        today = timezone.now().date()
        days_until_sunday = (6 - today.weekday()) % 7
        next_sunday = today + timedelta(days=days_until_sunday)

        updated_count = queryset.update(
            status='In Pulse',
            reveal_date=next_sunday
        )
        
        self.message_user(request, f'{updated_count} campaigns have been added to the Weekly Pulse for {next_sunday.strftime("%b %d, %Y")}.')

    add_to_next_pulse.short_description = "Add selected campaigns to next Pulse"    

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('funding', 'investor', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('funding__campaign_name', 'investor__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'message')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'funding', 'target_date', 'is_complete')
    list_filter = ('is_complete',)
    search_fields = ('title', 'funding__campaign_name')