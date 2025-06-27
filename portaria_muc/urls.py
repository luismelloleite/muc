from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from visitantes.views import VisitanteViewSet
from django.conf.urls import handler400, handler403, handler404, handler500
from .views import generic_error_view
from functools import partial
from django.conf import settings
from django.conf.urls.static import static

# API Router
router = DefaultRouter()
router.register(r'visitantes', VisitanteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('visitantes.urls', namespace='visitantes')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='visitantes:visitante_list'), name='logout'),
    path('admin/logout/', RedirectView.as_view(url='/logout/', permanent=True)),
]

# Serve static files during development and in production
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # For production/PyInstaller builds, also add static file serving
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler400 = partial(generic_error_view, status_code=400)
handler403 = partial(generic_error_view, status_code=403)
handler404 = partial(generic_error_view, status_code=404)
handler500 = partial(generic_error_view, status_code=500)
