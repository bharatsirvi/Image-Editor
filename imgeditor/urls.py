from django.contrib import admin
from django.urls import path,include
from imgeditor import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index,name="index"),
    path('home', views.home,name="home"),
    path('crop',views.crop,name='crop'),
    path('flip',views.flip,name='flip'),   
    path('contact',views.contact,name="contact"),
    path('about',views.about,name="about"),
    path('services',views.services,name="services"),
    path('dimensions',views.dimensions,name="dimensions"),
    path('percentage',views.percentage,name="percentage"),
    path('fliprotate',views.fliprotate,name="fliprotate"),
    path('crop_reset',views.crop_reset,name="crop_reset"),
    path('resize',views.resize,name="resize"),
    path('reset',views.reset,name="reset")   ,
    path('reupload',views.reupload,name="reupload"),
    path('compressor',views.compressor,name="compressor"), 
    path('compress',views.compress, name="compress"),
    path('down_compress',views.down_compress,name="down_compress"),
    path('filter',views.filter,name="filter"),
    path('adjust',views.adjust,name="adjust"),
    path("apply_filter", views.apply_filter, name="apply_filter"),
    path("down_filter",views.down_filter, name="down_filter"),
    path("down_resize",views.down_resize, name="down_resize")
]
