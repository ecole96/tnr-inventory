from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',login_required(views.PartsView.as_view()),name='parts'),
    path('new/',login_required(views.NewPart.as_view()),name='new_part'),
    path('edit/<int:pk>',login_required(views.EditPart.as_view()),name='edit_part'),
    path('delete/<int:pk>',login_required(views.DeletePart.as_view()),name='delete_part'),
    path('get_data/<int:pk>',views.get_part_data,name='get_part_data'),
    path('view_jobparts/<int:pk>',login_required(views.ViewJobParts.as_view()),name='view_jobparts')
]