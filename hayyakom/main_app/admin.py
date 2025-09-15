from django.contrib import admin
from .models import Profile, Company, Funding, Investment, Notification

class FundingAdmin(admin.ModelAdmin):
    list_filter = ['is_approved', 'status']    
    list_display = ('campaign_name', 'company', 'status', 'is_approved')    
    actions = ['approve_campaigns']

    def approve_campaigns(self, request, queryset):
        for campaign in queryset:
            campaign.is_approved = True
            campaign.save()            
            Notification.objects.create(
                user=campaign.company.owner,
                message=f"Congratulations! Your campaign '{campaign.campaign_name}' has been approved.",
                related_funding=campaign
            )
    
    approve_campaigns.short_description = "Approve selected campaigns"


admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Investment)
admin.site.register(Notification)
admin.site.register(Funding, FundingAdmin)