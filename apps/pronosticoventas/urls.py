from django.conf.urls import url
from . import views   #el punto indica que voy a buscar en el mismo lugar
from .views import VisualizarScoreClientes
from .views import VisualizarRNATrain
#from .views import VisualizarResultado
from .views import cons_score_cliente
from .views import guardarScore
from .views import eliminarScore
#from .views import entrenarRNA
from .views import VisualizarReporte
from .views import consReporte

urlpatterns = [
    url(r'^rnatrain/$', VisualizarRNATrain.as_view(),name="rnatrain"),
    url(r'^reporte/$', VisualizarReporte.as_view(), name="reporte"),
    #url(r'^rnamain/$', entrenarRNA,name="entrenarRNA"),
    #url(r'^resultado/$',VisualizarResultado,name="resultado"),
    url(r'^score_main/$', VisualizarScoreClientes,name="scoreclientes"),
    url(r'^score_cliente/$',cons_score_cliente,name ="cons_score"),
    url(r'^guardar/$',guardarScore),
    url(r'^eliminar/$',eliminarScore),

    url(r'^consReporte/$',consReporte),

]

