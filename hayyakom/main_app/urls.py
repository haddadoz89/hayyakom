from django.urls import path
from . import views

urlpatterns = [
    # --- General Site URLs ---
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.NotificationList.as_view(), name='notification_list'),
    # --- Funding Campaign URLs ---
    path('fundings/', views.FundingList.as_view(), name='funding_list'),
    path('fundings/create/', views.FundingCreate.as_view(), name='funding_create'),
    path('fundings/<int:pk>/', views.FundingDetail.as_view(), name='funding_detail'),
    path('fundings/<int:pk>/update/', views.FundingUpdate.as_view(), name='funding_update'),
    # --- Company URLs ---
    path('company/create/', views.CompanyCreate.as_view(), name='company_create'),
    path('company/<int:pk>/', views.CompanyDetail.as_view(), name='company_detail'),
    path('company/update/', views.CompanyUpdate.as_view(), name='company_update'),
    path('company/delete/', views.CompanyDelete.as_view(), name='company_delete'),
    # --- Investment & Payment URLs ---
    path('fundings/<int:funding_id>/add_investment/', views.add_investment, name='add_investment'),
    path('investment/success/', views.investment_success, name='investment_success'),
    path('investment/cancel/', views.investment_cancel, name='investment_cancel'),
    # --- Roadmap & Milestone URLs ---
    path('fundings/<int:funding_id>/manage_roadmap/', views.manage_roadmap, name='manage_roadmap'),
    path('milestones/<int:milestone_id>/complete/', views.mark_milestone_complete, name='mark_milestone_complete'),
    # --- weekly_pulse ---
    path('pulse/', views.weekly_pulse, name='weekly_pulse'),
    path('pulse/<int:funding_id>/show_interest/', views.show_interest, name='show_interest'),
    # --- Auth URLs ---
    path('accounts/signup/', views.signup, name='signup'),
]