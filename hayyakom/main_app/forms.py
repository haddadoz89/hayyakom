# main_app/forms.py

from django.forms import ModelForm
from .models import Company, Investment, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CompanyForm(ModelForm):
  class Meta:
    model = Company
    fields = ['company_name', 'cr_number']

class CustomSignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('Owner', 'Business Owner'), ('Investor', 'Investor')])
    phone_number = forms.CharField(max_length=20, label="Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 2000:
            raise forms.ValidationError("The minimum investment is 2000 BD.")
        if amount > 5000:
            raise forms.ValidationError("The maximum investment is 5000 BD.")
        return amount
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number']