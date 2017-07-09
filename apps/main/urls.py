from django.conf.urls import url
#from . import views   #el punto indica que voy a buscar en el mismo lugar
from .views import HomeView
from .views import ConfigView
from .views import ImportView
from .views import consSQL
from .views import guardarMongoAjax



urlpatterns = [
	url(r'^$', HomeView.as_view(), name="home"),
    url(r'^configuracion/$', ConfigView.as_view(), name="config"),
    url(r'^importacion/$', ImportView.as_view(), name="import"),
    url(r'^consSQL/$',consSQL),
    url(r'^guardarMongo/$',guardarMongoAjax),


]
