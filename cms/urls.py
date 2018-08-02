"""cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog import views
from rest_framework.authtoken import views as rest_framework

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', rest_framework.obtain_auth_token),
    path('', views.ApiRoot.as_view(), name=views.ApiRoot.name),
    path('profiles/', views.ProfileList.as_view(), name=views.ProfileList.name),
    path('profiles/<int:pk>/', views.ProfileDetail.as_view(), name=views.ProfileDetail.name),
    path('profiles/<int:user_pk>/posts/', views.ProfilePostList.as_view(), name=views.ProfilePostList.name),
    path('profiles/<int:user_pk>/posts/<int:pk>/', views.ProfilePostDetail.as_view(), name=views.ProfilePostDetail.name),

    path('profiles/<int:user_pk>/posts/<int:post_pk>/comments/', views.ProfilePostCommentList.as_view(),
         name=views.ProfilePostCommentList.name),
    path('profiles/<int:user_pk>/posts/<int:post_pk>/comments/<int:pk>/', views.ProfilePostCommentDetail.as_view(),
         name=views.ProfilePostCommentDetail.name),
    path('profile-posts/', views.ProfilePostAllList.as_view(), name=views.ProfilePostAllList.name),
    path('info-posts/', views.InfoPostList.as_view(), name=views.InfoPostList.name),
    path('import/', views.ImportaDB),
]
