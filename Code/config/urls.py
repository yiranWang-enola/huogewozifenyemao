"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from assessment import views # 从assessment应用中导入views模块

urlpatterns = [
    path('admin/', admin.site.urls), # 设置admin路径对应的视图函数为admin.site.urls
    path('', views.index, name='index'), # 设置根路径对应的视图函数为index
    path('api/data/', views.get_data, name='get_data'), # 设置api/data/路径对应的视图函数为get_data
]

