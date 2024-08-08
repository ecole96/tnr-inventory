from django.urls import path, re_path
from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required

# URL paths for all views relating to Job operations
urlpatterns = [
    path('',login_required(views.JobsView.as_view()),name='jobs'),
    path('new',login_required(views.NewJob.as_view()),name='new_job'),
    path('details/<int:pk>',login_required(views.JobDetails.as_view()),name='job_details'),
    path('details/edit_job/<int:pk>',login_required(views.EditJob.as_view()),name='edit_job'),
    path('details/delete_job/<int:pk>',login_required(views.DeleteJob.as_view()),name='delete_job'),
    path('details/new_service/<int:job_pk>',login_required(views.NewService.as_view()),name='new_service'),
    path('details/edit_service/<int:pk>',login_required(views.EditService.as_view()),name='edit_service'),
    path('details/delete_service/<int:pk>',login_required(views.DeleteService.as_view()),name='delete_service'),
    path('details/new_part/<int:job_pk>',login_required(views.NewJobPart.as_view()),name='new_jobpart'),
    path('details/edit_part/<int:pk>',login_required(views.EditJobPart.as_view()),name='edit_jobpart'),
    path('details/remove_part/<int:pk>',login_required(views.DeleteJobPart.as_view()),name='delete_jobpart'),
    path('details/new_part_singleuse/<int:job_pk>',login_required(views.NewJobPart_SingleUse.as_view()),name='new_jobpart_singleuse'),
    path('details/edit_part_singleuse/<int:pk>',login_required(views.EditJobPart_SingleUse.as_view()),name='edit_jobpart_singleuse'),
    path('details/remove_part_singleuse/<int:pk>',login_required(views.DeleteJobPart_SingleUse.as_view()),name='delete_jobpart_singleuse'),
    path('view_invoice/<int:job_pk>',views.view_invoice,name='view_invoice'),
    url(r'^jobpart_autocomplete/$',views.JobPartAutocomplete.as_view(),name='jobpart_autocomplete')
]