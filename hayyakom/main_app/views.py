# --- Imports ---
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Funding, Company, Investment, Milestone, Profile, Notification
from django.utils import timezone
from datetime import timedelta
from .forms import (
    CustomSignUpForm, InvestmentForm, UserUpdateForm, 
    ProfileUpdateForm, FundingFilterForm, MilestoneForm
)

# --- Global Configurations ---
stripe.api_key = settings.STRIPE_SECRET_KEY
BHD_TO_USD_RATE = 2.65265

# ============================================================================
# home page
# ============================================================================

def home(request):
    fundings = Funding.objects.filter(status='In Process', is_approved=True)
    
    query = request.GET.get('query')
    category = request.GET.get('category')

    if query:
        fundings = fundings.filter(
            Q(campaign_name__icontains=query) | Q(company__company_name__icontains=query)
        ).distinct()

    if category:
        fundings = fundings.filter(category=category)

    form = FundingFilterForm(request.GET)
    context = {
        'fundings': fundings.order_by('-end_date'),
        'form': form
    }
    return render(request, 'home.html', context)


# ============================================================================
# Funding Campaign Views
# ============================================================================

class FundingList(LoginRequiredMixin, ListView):
    model = Funding
    template_name = 'fundings/index.html'

    def get_queryset(self):
        try:
            profile = self.request.user.profile
        except Profile.DoesNotExist:
            return Funding.objects.filter(status='In Process', is_approved=True)

        if profile.role == 'Owner':
            try:
                return Funding.objects.filter(company=self.request.user.company).order_by('-end_date')
            except Company.DoesNotExist:
                return Funding.objects.none()
        else:
            return Funding.objects.none()
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.profile.role == 'Investor':
            context['my_investments'] = Investment.objects.filter(investor=self.request.user).order_by('-id')
        return context

class FundingDetail(DetailView):
    model = Funding
    template_name = 'fundings/detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not obj.is_approved and obj.company.owner != self.request.user:
            raise Http404("Campaign not found or not approved.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_investor = False
        if self.request.user.is_authenticated:
            if self.object.investment_set.filter(investor=self.request.user).exists():
                is_investor = True
        context['is_investor'] = is_investor
        return context

class FundingCreate(LoginRequiredMixin, CreateView):
    model = Funding
    fields = ['campaign_name', 'description', 'goal', 'end_date', 'category']
    template_name = 'fundings/funding_form.html'
    success_url = '/fundings/'

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        response = super().form_valid(form)
        Notification.objects.create(
            user=self.request.user,
            message=f"Your new campaign '{self.object.campaign_name}' has been successfully submitted for admin review.",
            related_funding=self.object
        )
        return response

class FundingUpdate(LoginRequiredMixin, UpdateView):
    model = Funding
    fields = ['campaign_name', 'description', 'category']
    template_name = 'fundings/funding_form.html'
    success_url = '/fundings/'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company=self.request.user.company)
# ============================================================================
# Company Views
# ============================================================================

class CompanyDetail(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company/company_detail.html' 

class CompanyCreate(LoginRequiredMixin, CreateView):
    model = Company
    fields = ['company_name', 'cr_number']
    template_name = 'company/company_form.html'
    success_url = '/fundings/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class CompanyUpdate(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['company_name', 'cr_number']
    template_name = 'company/company_form.html'
    success_url = '/fundings/'

    def get_object(self):
        return self.request.user.company

class CompanyDelete(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'company/company_confirm_delete.html'
    success_url = '/'

    def get_object(self):
        return self.request.user.company
    
    def post(self, request, *args, **kwargs):
        company = self.get_object()
        for funding in company.funding_set.all():
            if funding.total_invested() > 0:
                messages.error(request, 'Cannot delete company with active investments in its campaigns.')
                return redirect('company_detail', pk=company.pk)
        
        messages.success(request, f'Company "{company.company_name}" has been deleted.')
        return super().post(request, *args, **kwargs)


# ============================================================================
# Investment & Payment Views
# ============================================================================

@login_required
def add_investment(request, funding_id):
    funding = get_object_or_404(Funding, id=funding_id)

    if funding.status == 'Completed':
        messages.error(request, 'This funding campaign has already been completed and is no longer accepting investments.')
        return redirect('funding_detail', pk=funding_id)

    if Investment.objects.filter(investor=request.user, funding=funding).exists():
        messages.error(request, 'You have already invested in this campaign.')
        return redirect('funding_detail', pk=funding_id)

    form = InvestmentForm(request.POST or None, funding=funding)
    if request.method == 'POST':
        if form.is_valid():
            amount_in_bhd = form.cleaned_data.get('amount')
            amount_in_usd = amount_in_bhd * BHD_TO_USD_RATE
            amount_in_cents = int(amount_in_usd * 100)
            
            try:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {'name': f"Investment in: {funding.campaign_name}"},
                            'unit_amount': amount_in_cents,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri('/investment/success/') + f'?session_id={{CHECKOUT_SESSION_ID}}&funding_id={funding_id}&amount={amount_in_bhd}',
                    cancel_url=request.build_absolute_uri('/investment/cancel/'),
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(request, f"Something went wrong with the payment process: {e}")
                return redirect(funding.get_absolute_url())
    
    return render(request, 'investment/investment_form.html', {'form': form, 'funding': funding})

def investment_success(request):
    session_id = request.GET.get('session_id')
    funding_id = request.GET.get('funding_id')
    amount_str = request.GET.get('amount')
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            if not Investment.objects.filter(investor=request.user, funding_id=funding_id).exists():
                funding = get_object_or_404(Funding, id=funding_id)
                current_total_invested = funding.total_invested()
                new_investment_amount = int(amount_str)
                new_investment = Investment.objects.create(
                    investor=request.user,
                    funding=funding,
                    amount=new_investment_amount
                )
                owner = funding.company.owner
                investor_name = request.user.first_name
                Notification.objects.create(
                    user=owner,
                    message=f"{investor_name} invested {new_investment.amount} BD in your campaign '{funding.campaign_name}'.",
                    related_funding=funding
                )
                Notification.objects.create(
                    user=request.user,
                    message=f"Thank you! Your investment of {new_investment.amount} BD in '{funding.campaign_name}' has been confirmed.",
                    related_funding=funding
                )
                new_total = current_total_invested + new_investment_amount

                if new_total >= funding.goal and funding.status != 'Completed':
                    funding.status = 'Completed'
                    funding.save()
                else:
                    messages.success(request, 'Your investment was successful!')
            else:
                messages.info(request, 'This investment has already been recorded.')
        else:
            messages.error(request, 'Payment was not successful. Please try again.')   
    except Exception as e:
        messages.error(request, f"An error occurred while verifying your payment: {e}")

    return render(request, 'investment/success.html')

def investment_cancel(request):
    return render(request, 'investment/cancel.html')

# ============================================================================
# User & Profile Views
# ============================================================================

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data.get('role'),
                phone_number=form.cleaned_data.get('phone_number')
            )
            login(request, user)
            return redirect('funding_list')
        else:
            error_message = 'Invalid sign up - try again'
    form = CustomSignUpForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile.html', context)


# ============================================================================
# Notification & Roadmap Views
# ============================================================================

class NotificationList(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user).order_by('-created_at')
        queryset.filter(is_read=False).update(is_read=True)
        return queryset

@login_required
def manage_roadmap(request, funding_id):
    funding = get_object_or_404(Funding, id=funding_id)
    if request.user != funding.company.owner:
        raise PermissionDenied
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            new_milestone = form.save(commit=False)
            new_milestone.funding = funding
            new_milestone.save()
            messages.success(request, 'New milestone added successfully!')
            return redirect('manage_roadmap', funding_id=funding.id)
    else:
        form = MilestoneForm()

    milestones = funding.milestone_set.all()
    context = {'funding': funding, 'milestones': milestones, 'form': form}
    return render(request, 'fundings/manage_roadmap.html', context)

@login_required
def mark_milestone_complete(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    if request.user != milestone.funding.company.owner:
        raise PermissionDenied

    if request.method == 'POST':
        milestone.is_complete = True
        milestone.save()
        investments = milestone.funding.investment_set.all()
        for investment in investments:
            Notification.objects.create(
                user=investment.investor,
                message=f"A milestone has been completed for '{milestone.funding.campaign_name}': {milestone.title}",
                related_funding=milestone.funding
                )
        messages.success(request, f'Milestone "{milestone.title}" marked as complete!')
    return redirect('manage_roadmap', funding_id=milestone.funding.id)
# ============================================================================
# Weekly pulse
# ============================================================================
def weekly_pulse(request):

    today = timezone.now().date()
    days_since_sunday = (today.weekday() + 1) % 7
    current_sunday = today - timedelta(days=days_since_sunday)
    
    pulse_campaigns = Funding.objects.filter(
        status='In Pulse',
        reveal_date=current_sunday
    )

    context = {
        'pulse_campaigns': pulse_campaigns,
        'today': today,
        'current_sunday': current_sunday,
    }
    return render(request, 'pulse/weekly_pulse.html', context)
@login_required
def show_interest(request, funding_id):
    if request.method == 'POST':
        funding = get_object_or_404(Funding, id=funding_id)
        funding.interested_users.add(request.user)
    return redirect('weekly_pulse')