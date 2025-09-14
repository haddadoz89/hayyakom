from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Funding, Company, Investment, Profile
from django.contrib.auth import login
from .forms import CompanyForm, CustomSignUpForm, InvestmentForm, UserUpdateForm, ProfileUpdateForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

def home(request):
    fundings = Funding.objects.filter(status='In Process')
    return render(request, 'home.html', {'fundings': fundings})

class FundingList(ListView):
    model = Funding
    template_name = 'fundings/index.html'

    def get_queryset(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        if profile.role == 'Owner':
            try:
                company = Company.objects.get(owner=self.request.user)
                return Funding.objects.filter(company=company)
            except Company.DoesNotExist:
                return Funding.objects.none()
        return Funding.objects.filter(status='In Process')

class FundingDetail(DetailView):
    model = Funding
    template_name = 'fundings/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the logged-in user has invested in this specific campaign
        is_investor = False
        if self.request.user.is_authenticated:
            if self.object.investment_set.filter(investor=self.request.user).exists():
                is_investor = True
        context['is_investor'] = is_investor
        return context

class FundingCreate(LoginRequiredMixin, CreateView):
    model = Funding
    fields = ['campaign_name', 'description', 'goal', 'end_date']
    template_name = 'fundings/funding_form.html'

    def form_valid(self, form):
        company = Company.objects.get(owner=self.request.user)
        form.instance.company = company
        return super().form_valid(form)

class FundingUpdate(LoginRequiredMixin, UpdateView):
    model = Funding
    fields = ['campaign_name', 'description', 'end_date']
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

def add_investment(request, funding_id):
    funding = get_object_or_404(Funding, id=funding_id)
    if Investment.objects.filter(investor=request.user, funding=funding).exists():
        messages.error(request, 'You have already invested in this campaign.')
        return redirect('funding_detail', pk=funding_id)
    form = InvestmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_investment = form.save(commit=False)
            new_investment.investor = request.user
            new_investment.funding = funding
            new_investment.save()
            messages.success(request, 'Your investment was successful!') # <-- Optional success message
            return redirect('funding_list')
            
    return render(request, 'investment/investment_form.html', {'form': form, 'funding': funding})

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
    success_url = '/fundings/' # Redirect to dashboard after creation

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class CompanyUpdate(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/company_form.html'
    success_url = '/fundings/' # Redirect to dashboard after update

    def get_object(self):
        # This ensures the user can only edit their own company
        return self.request.user.company

class CompanyDelete(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'company/company_confirm_delete.html'
    success_url = '/' # Redirect to home page after successful deletion

    def get_object(self):
        # This ensures the user can only access their own company's delete page
        return self.request.user.company
    
    def post(self, request, *args, **kwargs):
        company = self.get_object()
        # Check if any funding campaign for this company has investments
        for funding in company.funding_set.all():
            if funding.total_invested() > 0:
                messages.error(request, 'Cannot delete company with active investments in its campaigns.')
                return redirect('company_detail', pk=company.pk)
        
        # If the check passes, proceed with deletion
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