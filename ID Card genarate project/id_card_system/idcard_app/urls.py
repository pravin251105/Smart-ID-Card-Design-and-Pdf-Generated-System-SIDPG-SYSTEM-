from django.urls import path
from . import views
from .views import save_template


urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),

    path("user/dashboard/", views.user_dashboard, name="user_dashboard"),

    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/profile/", views.admin_profile, name="admin_profile"),
    path("admin/users/", views.manage_users, name="manage_users"),
    path("admin/users/api/list/", views.get_users_json, name="get_users_json"),
    path("admin/users/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("admin/templates/", views.template_admin, name="template_admin"),
    path("admin/templates/debug/", views.show_template_debug, name="template_debug"),
    # Designer API
    path("admin/templates/api/save/", views.save_design, name="save_design"),
    path("admin/templates/api/list/", views.list_designs, name="list_designs"),
    path("admin/templates/api/load/<int:design_id>/", views.load_design, name="load_design"),
    path("admin/templates/api/batch-export/", views.batch_export, name="batch_export"),
    path("admin/generate-id/", views.generate_id_card, name="generate_id_card"),
    path("admin/generate-id/api/templates/", views.get_id_templates, name="get_id_templates"),
    path("admin/generate-id/api/templates/<int:template_id>/", views.get_id_template_detail, name="get_id_template_detail"),
    path("admin/generate-id/api/templates/<int:template_id>/delete/", views.delete_id_template, name="delete_id_template"),
    path("admin/generate-id/api/debug/", views.template_debug, name="api_template_debug"),
    path("api/test/", views.test_api, name="test_api"),  # Test endpoint for debugging
    path("api/photo/remove-bg/<int:user_id>/", views.remove_background_api, name="remove_background_api"),
    path("admin/dashboard-settings/", views.dashboard_settings, name="dashboard_settings"),
    path("save-template/", save_template, name="save_template"),
    path("templates/list/", views.load_templates, name="load_templates"),


]
