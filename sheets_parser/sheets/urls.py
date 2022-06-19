from django.urls import path

from .views import start_update, stop_update, view_date

urlpatterns = [
    path('', view_date, name='view_data'),
    path('start_update/', start_update, name='start_update'),
    path('stop_update/', stop_update, name='stop_update'),

]