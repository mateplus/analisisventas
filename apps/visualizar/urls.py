from django.conf.urls import url
#from . import views   #el punto indica que voy a buscar en el mismo lugar
from .views import VisualizarView
from .views import consVentasGeneral

urlpatterns = [
    url(r'^visualizar/$', VisualizarView.as_view(),name="ventas"),
    url(r'^visualizar/consgeneral/$',consVentasGeneral,name="consVentasGeneral"),
]
