import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Funding, Company, Investment, Profile, Notification
from django.contrib.auth import login
from .forms import CompanyForm, CustomSignUpForm, InvestmentForm, UserUpdateForm, ProfileUpdateForm, FundingFilterForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Q

stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required
def investment_success(request):
    session_id = request.GET.get('session_id')
    funding_id = request.GET.get('funding_id')
    amount = request.GET.get('amount')
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            if not Investment.objects.filter(investor=request.user, funding_id=funding_id).exists():
                funding = get_object_or_404(Funding, id=funding_id)
                new_investment = Investment.objects.create(
                    investor=request.user,
                    funding=funding,
                    amount=int(amount)
                )
                
                campaign_owner = funding.company.owner
                investor_name = request.user.first_name or request.user.username
                Notification.objects.create(
                    user=campaign_owner,
                    message=f"{investor_name} invested {new_investment.amount} BD in your campaign '{funding.campaign_name}'.",
                    related_funding=funding
                )
                
                messages.success(request, 'Your investment was successful!')
            else:
                messages.info(request, 'This investment has already been recorded.')

        else:
            messages.error(request, 'Payment was not successful. Please try again.')

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")

    return render(request, 'investment/success.html')

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

class FundingList(ListView):
    model = Funding
    template_name = 'fundings/index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            profile = self.request.user.profile
            if profile.role == 'Owner':
                queryset = Funding.objects.filter(company=self.request.user.company)
            else:
                queryset = Funding.objects.filter(status='In Process', is_approved=True)
        except (Profile.DoesNotExist, Company.DoesNotExist):
            queryset = Funding.objects.filter(status='In Process', is_approved=True)

        query = self.request.GET.get('query')
        category = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(
                Q(campaign_name__icontains=query) | Q(company__company_name__icontains=query)
            ).distinct()

        if category:
            queryset = queryset.filter(category=category)
            
        return queryset.order_by('-end_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FundingFilterForm(self.request.GET)
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

    def form_valid(self, form):
        company = Company.objects.get(owner=self.request.user)
        form.instance.company = company
        return super().form_valid(form)

class FundingUpdate(LoginRequiredMixin, UpdateView):
    model = Funding
    fields = ['campaign_name', 'description', 'end_date', 'category']
    template_name = 'fundings/funding_form.html'

class FundingDelete(LoginRequiredMixin, DeleteView):
    model = Funding
    success_url = '/fundings/'
    template_name = 'fundings/funding_confirm_delete.html'
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.investment_set.count() > 0:
            messages.error(request, 'Cannot delete a campaign that has active investments.')
            return redirect('funding_detail', pk=self.object.pk)        
        return super().post(request, *args, **kwargs)

@login_required
def add_investment(request, funding_id):
    funding = get_object_or_404(Funding, id=funding_id)

    if Investment.objects.filter(investor=request.user, funding=funding).exists():
        messages.error(request, 'You have already invested in this campaign.')
        return redirect('funding_detail', pk=funding_id)

    form = InvestmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            
            bhd_to_usd_rate = 2.65265
            amount_in_usd = amount * bhd_to_usd_rate
            amount_in_cents = int(amount_in_usd * 100) # Stripe needs cents
            
            try:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': f"Investment in: {funding.campaign_name}",
                                },
                                'unit_amount': amount_in_cents,
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url=request.build_absolute_uri('/investment/success/') + f'?session_id={{CHECKOUT_SESSION_ID}}&funding_id={funding_id}&amount={amount}',
                    cancel_url=request.build_absolute_uri(funding.get_absolute_url()),
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(request, f"Something went wrong with the payment process: {e}")
                return redirect(funding.get_absolute_url())
    
    return render(request, 'investment/investment_form.html', {'form': form, 'funding': funding})

@login_required
def investment_success(request):
    session_id = request.GET.get('session_id')
    funding_id = request.GET.get('funding_id')
    amount = request.GET.get('amount')
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            if not Investment.objects.filter(investor=request.user, funding_id=funding_id).exists():
                funding = get_object_or_404(Funding, id=funding_id)                
                new_investment = Investment.objects.create(
                    investor=request.user,
                    funding=funding,
                    amount=int(amount)
                )                
                owner = funding.company.owner
                investor_name = request.user.first_name or request.user.username
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

class InvestmentUpdate(LoginRequiredMixin, UpdateView):
    model = Investment
    form_class = InvestmentForm
    template_name = 'investment/investment_form.html'
    success_url = '/fundings/' # Redirect to dashboard after update

    def get_queryset(self):
        return super().get_queryset().filter(investor=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        investment = self.get_object()
        if investment.funding.status != 'In Process':
            messages.error(request, 'This investment cannot be modified as the campaign is no longer active.')
            return redirect('funding_list')
        return super().dispatch(request, *args, **kwargs)


class InvestmentDelete(LoginRequiredMixin, DeleteView):
    model = Investment
    template_name = 'investment/investment_confirm_delete.html'
    success_url = '/fundings/'

    def get_queryset(self):
        return super().get_queryset().filter(investor=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        investment = self.get_object()
        if investment.funding.status != 'In Process':
            messages.error(request, 'This investment cannot be deleted as the campaign is no longer active.')
            return redirect('funding_list')
        return super().dispatch(request, *args, **kwargs)


class CompanyDetail(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company/company_detail.html' 

class CompanyCreate(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/company_form.html'
    success_url = '/fundings/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class CompanyUpdate(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
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

class NotificationList(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user).order_by('-created_at')
        queryset.filter(is_read=False).update(is_read=True)
        return queryset

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