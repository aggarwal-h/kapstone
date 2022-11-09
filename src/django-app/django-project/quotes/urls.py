from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'quotes', views.QuoteViewSet)
router.register(r'quote-requests', views.QuoteRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]