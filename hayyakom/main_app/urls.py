from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.NotificationList.as_view(), name='notification_list'),
    path('fundings/', views.FundingList.as_view(), name='funding_list'),
    path('fundings/create/', views.FundingCreate.as_view(), name='funding_create'),
    path('fundings/<int:pk>/', views.FundingDetail.as_view(), name='funding_detail'),
    path('fundings/<int:pk>/update/', views.FundingUpdate.as_view(), name='funding_update'),
    path('company/create/', views.CompanyCreate.as_view(), name='company_create'),
    path('company/<int:pk>/', views.CompanyDetail.as_view(), name='company_detail'),
    path('company/update/', views.CompanyUpdate.as_view(), name='company_update'),
    path('company/delete/', views.CompanyDelete.as_view(), name='company_delete'),
    path('fundings/<int:funding_id>/add_investment/', views.add_investment, name='add_investment'),
    path('investment/success/', views.investment_success, name='investment_success'),
    path('investment/cancel/', views.investment_cancel, name='investment_cancel'),
    path('investment/<int:pk>/update/', views.InvestmentUpdate.as_view(), name='investment_update'),
    path('investment/<int:pk>/delete/', views.InvestmentDelete.as_view(), name='investment_delete'),
    path('accounts/signup/', views.signup, name='signup'),
]