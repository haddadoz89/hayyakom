from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fundings/', views.FundingList.as_view(), name='funding_list'),
    path('fundings/<int:pk>/', views.FundingDetail.as_view(), name='funding_detail'),
    path('fundings/create/', views.FundingCreate.as_view(), name='funding_create'),
    path('fundings/<int:pk>/update/', views.FundingUpdate.as_view(), name='funding_update'),
    path('fundings/<int:pk>/delete/', views.FundingDelete.as_view(), name='funding_delete'),
    path('fundings/<int:funding_id>/add_investment/', views.add_investment, name='add_investment'),
    path('investment/<int:pk>/update/', views.InvestmentUpdate.as_view(), name='investment_update'),
    path('investment/<int:pk>/delete/', views.InvestmentDelete.as_view(), name='investment_delete'),
    path('company/<int:pk>/', views.CompanyDetail.as_view(), name='company_detail'),
    path('company/create/', views.CompanyCreate.as_view(), name='company_create'),
    path('accounts/signup/', views.signup, name='signup'),
    path('company/create/', views.CompanyCreate.as_view(), name='company_create'),
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]