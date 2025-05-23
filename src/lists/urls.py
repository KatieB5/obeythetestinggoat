"""
URL configuration for superlists project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from lists.views import home_page, view_list, new_list, my_lists, share_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home_page, name="home"),
    path("new", new_list, name="new_list"),
    path("<int:list_id>/", view_list, name="view_list"),
    path("users/<str:email>/", my_lists, name="my_lists"),
    path("<int:list_id>/share", share_list, name="share_list")
]
