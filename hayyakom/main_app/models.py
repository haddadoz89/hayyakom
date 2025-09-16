from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
# ============================================================================
# Choices Tuples
# ============================================================================
STATUS_CHOICES = (
    ('In Process', 'In Process'),
    ('Completed', 'Completed'),
    ('Failed', 'Failed'),
)

INVESTMENT_STATUS_CHOICES = (
    ('Pledged', 'Pledged'),
    ('Collected', 'Collected'),
    ('Returned', 'Returned'),
)

CATEGORY_CHOICES = (
    ('Technology', 'Technology'),
    ('Food & Beverage', 'Food & Beverage'),
    ('Retail', 'Retail'),
    ('Health & Wellness', 'Health & Wellness'),
    ('Arts & Culture', 'Arts & Culture'),
    ('Business', 'Business'),
    ('Other', 'Other'),
)
# ============================================================================
# User & Company Models
# ============================================================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('Owner', 'Owner'), ('Investor', 'Investor')])
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.first_name or self.user.username} ({self.role})"

class Company(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    cr_number = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name
# ============================================================================
# Funding & Investment Models
# ============================================================================
class Funding(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Process')
    is_approved = models.BooleanField(default=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')

    def __str__(self):
        return self.campaign_name

    def get_absolute_url(self):
        return reverse('funding_detail', kwargs={'pk': self.id})

    def total_invested(self):
        result = self.investment_set.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def progress_percentage(self):
        if self.goal > 0:
            return (self.total_invested() / self.goal) * 100
        return 0

class Investment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=INVESTMENT_STATUS_CHOICES, default='Pledged')

    def __str__(self):
        return f"{self.amount} by {self.investor.first_name} for {self.funding.campaign_name}"

# ============================================================================
# Feature-Specific Models
# ============================================================================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_funding = models.ForeignKey(Funding, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"

class Milestone(models.Model):
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    target_date = models.DateField()
    is_complete = models.BooleanField(default=False)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f"{self.title} for {self.funding.campaign_name}"