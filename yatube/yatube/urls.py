
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include(('posts.urls', 'posts'), namespace='posts')),
    path('auth/', include(('users.urls', 'users'), namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include(('about.urls', 'about'), namespace='about')),
    path('admin/', admin.site.urls),
]
