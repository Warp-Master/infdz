from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<uuid:exam_uuid>', views.ExamView.as_view(), name='exam')
]
