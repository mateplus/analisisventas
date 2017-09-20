from django.shortcuts import render
from django.views.generic import TemplateView
#from analisisventas.apps.main.models import Ventas
#from  django.apps.main.models import  Ventas
from apps.main.models import Ventas
from django.http import JsonResponse
from django.http import HttpResponse
from bson.json_util import dumps
import json
#from .apps.main.models import Ventas
import calendar

# Create your views here.
class VisualizarView(TemplateView):
    template_name='ventas.html'

#paraque devuelva el trimstre de cada mes
def ValTrim(x):
    return {
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2,
        7: 3,
        8: 3,
        9: 3,
        10:4,
        11:4,
        12:4
    }[x]


def consVentasGeneral(request):
    errors=[]
    context={}
    lista=[]
    listaxmes=[]
    try:
        #consulta de ventas totales por anios
        pipeline=[ {"$group":{ "_id":{"year": {"$year" : "$FechaTrans"}}, "PTotal":{"$sum":"$PTotal"}}}, {"$sort":{"_id.year":1}}]

        #{$sort : {"_id.year":1,"_id.mes":1 }}
        VentasxAnio= Ventas.objects.aggregate(*pipeline )
        for doc in VentasxAnio:
            d=dict(doc["_id"])
            lista.append( {'nombre':d['year'],'valor': doc["PTotal"] })

        cadena=dumps(lista)
        context['ventasxanio'] =cadena

        #consulta de ventas x mes
        pipeline=[ {"$group":{ "_id":{"year": {"$year" : "$FechaTrans"},"mes":{"$month":"$FechaTrans" } }, "PTotal":{"$sum":"$PTotal"}}}, {"$sort":{"_id.year":1,"_id.mes":1}}]

        VentasxMes= Ventas.objects.aggregate(*pipeline )

        #print( dumps(VentasxMes))

        for doc in VentasxMes:
            #esta linea fue necesaria porque caso contrario cambia el orden
            #parce que es necesario leer el objeto antes de  procesarlo
            #valor = doc
            #print(doc)
            d=dict(doc["_id"])
            #print(d['year'])

            listaxmes.append( {'Anio':d['year'], 'Mes': calendar.month_abbr[ d['mes']],'venta': doc["PTotal"],
                               'trimestre': ValTrim( d['mes']) })


        #print(listaxmes)
        cadena = dumps(listaxmes)
        context['ventasxmes']=cadena

        #print(  VentasxAnio.objects.max("Total"))

        #doc1 = VentasxAnio.objects.orderby("Total").limit(-1).first()
        #print( doc1["nombre"])

        #MyDocument.object().order_by("-max_column").limit(-1).first()

       # context['venta_resmen']= {"max": Ventas.objects.count, "maxDate": consFecha(request,1), "minDate": consFecha(request,0)}

    except Exception as e:
        errors.append(str(e))
        context['ventasxanio']= ''
        #context['dataY']= ''
    context['errors'] = errors
    #return JsonResponse(cadena,safe=False)

    return render(request,'ventas.html',context)
    #return HttpResponse(response.content)