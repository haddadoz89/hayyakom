from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Investment, Profile, Milestone, CATEGORY_CHOICES
# ============================================================================
# User & Auth Forms
# ============================================================================
class CustomSignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('Owner', 'Business Owner'), ('Investor', 'Investor')])
    phone_number = forms.CharField(max_length=20, label="Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']
# ============================================================================
# Funding & Investment Forms
# ============================================================================
class FundingFilterForm(forms.Form):
    CATEGORY_CHOICES_WITH_ALL = (('', 'All Categories'),) + CATEGORY_CHOICES
    query = forms.CharField(
        label='Search by name',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Campaign or company name...'})
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES_WITH_ALL,
        required=False
    )

class InvestmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.funding = kwargs.pop('funding', None)
        super(InvestmentForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Investment
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.funding:
            remaining_amount = self.funding.goal - self.funding.total_invested()
            if amount > remaining_amount:
                raise forms.ValidationError(
                    f"This investment would exceed the goal. The maximum you can invest is {remaining_amount} BD."
                )
            if remaining_amount < 2000:
                if amount != remaining_amount:
                    raise forms.ValidationError(
                        f"Only a final investment of exactly {remaining_amount} BD is needed to complete this campaign."
                    )
                return amount
        if amount < 2000:
            raise forms.ValidationError("The minimum investment is 2000 BD.")
        if amount > 5000:
            raise forms.ValidationError("The maximum investment is 5000 BD.")
        return amount
# ============================================================================
# Milestone Form
# ============================================================================
class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }