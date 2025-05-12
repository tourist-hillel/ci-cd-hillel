from django.urls import path
from storage_app.views import upload_files, file_list


urlpatterns = [
    path('', file_list, name='file_list'),
    path('upload/', upload_files, name='upload_files'),
]