from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
#from django.urls import reverse
from django.core.urlresolvers import reverse
from django.views.generic import FormView
from django.views.generic import TemplateView,RedirectView
#from .forms import ConfigForm
from .models import Configuracion
from .models import Ventas
from django.db.models import Avg, Max, Min, Sum
import time
import pyodbc
from datetime import date, datetime
from mongoengine.queryset.visitor import Q
#from mongoengine import fields, Document, EmbeddedDocument, aggregate

# Create your views here.
# Create your views here.
class HomeView(TemplateView):
	template_name='index.html'


#el codigo debe permitir modificar o crear un nuevo registro
#la configuracion nunca tendra mas de dos registros

class ConfigView(TemplateView):
    template_name='config.html'
    def post(self,request,*args,**kwargs):
     if 'btnGuardar' in request.POST:
        print("presiono guardar")
        try:
            obj=Configuracion.objects.get(0)
            obj.samiServer=  request.POST['samiServer']
            obj.usuarioSQL = request.POST['usuarioSQL']
            obj.passSQL = request.POST['passSQL']
            obj.Transacciones = request.POST['Transacciones']
            obj.baseDatosSQL = request.POST['baseDatosSQL']
            obj.IdentificadorTrans= request.POST['IdentificadorTrans']

        except:
            obj=Configuracion(samiServer=request.POST['samiServer'],
                              usuarioSQL= request.POST['usuarioSQL'],
                              passSQL= request.POST['passSQL'],
                              Transacciones= request.POST['Transacciones'],
                              baseDatosSQL=request.POST['baseDatosSQL'],
                              IdentificadorTrans=request.POST['IdentificadorTrans'],
                              )

        obj.save()
        return HttpResponseRedirect(reverse( 'main:home', **kwargs))
     else:
      msg =  TestSQL(request)
     #context['respuesta']= {'msg': msg }
     context={}
     #response= JsonResponse({'msg': msg })
     context['configuracion'] = {"samiServer":request.POST['samiServer'],
                                 "usuarioSQL":request.POST['usuarioSQL'],
                                 "passSQL":request.POST['passSQL'],
                                 "Transacciones":request.POST['Transacciones'],
                                 "baseDatosSQL":request.POST['baseDatosSQL'],
                                 "IdentificadorTrans":request.POST['IdentificadorTrans']}
     context['test']={'msg': msg }
     return render(request,'config.html', context)


    def get_context_data(self,**kwargs):
        context=super(ConfigView,self).get_context_data(**kwargs)
        try:
            context['configuracion'] = Configuracion.objects.first
        except:
            context['configuracion']=''
        return context

#subrutina pra probar los datos del servidor de SQL y verificar su conexion
def TestSQL(request):
        #print("estoy en Test")
        msg=''
        server=   request.POST['samiServer']
        username=   request.POST['usuarioSQL']
        password=   request.POST['passSQL']
        trans=   request.POST['Transacciones']
        database=   request.POST['baseDatosSQL']
        driver= '{ODBC Driver 13 for SQL Server}'
        if len(server) != 0 and len(username) !=0 and len(password) !=0 and len(database) != 0:
            try:
                cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
                cursor = cnxn.cursor()
                msg=  'Conexion a base de datos realizada con exito'
                #ahorabamos a probar si exsite el  codigo de transacciones
                sql ="Select top 1 GNC.CodTrans from GNComprobante GNC  "  \
                     "where GNC.Estado <> 3 and  CodTrans = '" +  trans +  "'"
                #print(sql)
                cursor.execute(sql)
                datos = dictfetchall(cursor)
                if bool(datos) :
                    msg = msg + ' se han encontrado transacciones'
                else:
                    msg = msg + ' No se han encontrado transacciones revise el codigo'
            except Exception as e:
                msg=  'error en conexion: ' + str(e)
        else :
            msg='Debe ingresar la informacion de la base de datos para poder probar su conexion!!'

        return msg


def consFecha(self,bandMax):
    if bandMax==1:
        pipeline=[ {"$group":{ "_id":"", "res":{"$max":"$FechaTrans"}} } ]
    else:
        pipeline=[ {"$group":{ "_id":"", "res":{"$min":"$FechaTrans"}} } ]

    max= Ventas.objects.aggregate(*pipeline )
    resultado=list(max)

    return resultado[0]['res']


class ImportView(TemplateView):

    template_name='import.html'

    #initial={'fdesde': time.strftime("%d/%m/%y"), 'fhasta':time.strftime("%d/%m/%y")}

    def get_context_data(self,**kwargs):
        errors=[]
        context=super(ImportView,self).get_context_data(**kwargs)

        if not context.get('condicion:fdesde'):
            context['condicion']={'fdesde':time.strftime("%d/%m/%Y"),'fhasta': time.strftime("%d/%m/%Y") }
        try:
            obj=Configuracion.objects.get(0)

            context['configuracion_sql'] = {"server":obj.samiServer,"database":obj.baseDatosSQL, "username":obj.usuarioSQL,"transacciones":obj.Transacciones}


        except Exception as e:
            errors.append(str(e))
        #------------------------------------------- consulta datos ventasa base de mongo DB -------------------------------------------------------
        try:
            context["configuracion_mongo"]={"numMongo": Ventas.objects.count, "maxDate": consFecha(self,1), "minDate": consFecha(self,0)}
        except Exception as e:
            errors.append(str(e))

        context['errors'] = errors
        return context



def consSQL(request):
    context={}
    errors=[]
    try:
        obj=Configuracion.objects.get(0)
        server = obj.samiServer
        database = obj.baseDatosSQL
        username = obj.usuarioSQL
        password = obj.passSQL

        driver= '{ODBC Driver 13 for SQL Server}'
        cnxn = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        context['configuracion_sql'] = {"server":obj.samiServer,"database":obj.baseDatosSQL, "username":obj.usuarioSQL,"transacciones":obj.Transacciones}

                                    #"numMongo": Ventas.objects.count, "maxDate": consFecha(request,1), "minDate": consFecha(request,0) }
        #print("primer try OK")
        if 'fdesde' in request.GET and 'fhasta' in request.GET :
            fdesde=request.GET['fdesde']
            fhasta=request.GET['fhasta']
            if not fdesde:
                errors.append('fecha desde invalida')
            else:
                #cursor.execute("select CodTrans,NumTrans,Nombre,FechaTrans from GNComprobante where FechaTrans between  '" + fdesde
                #               + "' and  '" + fhasta + "' and  CodTrans = '" +  obj.Transacciones +  "'" )
                try:
                    sql ="Select GNC.CodTrans, GNC.NumTrans,GNC.NumDocRef, GNC.FechaTrans, FCVendedor.CodVendedor as vendedor, \
                    PCProvCli.RUC, PCProvCli.Nombre,PCProvCli.Direccion1,PCProvCli.Telefono1, PCProvCli.Pais, \
                    PCProvCli.Ciudad,PCProvCli.Provincia,PCGrupo1.CodGrupo1, PCGrupo2.CodGrupo2 ,PCGrupo3.CodGrupo3, \
                    sum( IVKArdex.PrecioRealTotal) *-1 as Total \
                    from GNComprobante GNC left join FCVendedor on GNC.IdVendedor = FCVendedor.IdVendedor \
                    inner join PCProvCli on GNC.IdClienteRef = PCProvCli.IdProvCli left join PCGrupo1 on Pcgrupo1.IdGrupo1 = PCProvCli.IdGrupo1 \
                    left join PCGrupo2 on Pcgrupo2.IdGrupo2 = PCProvCli.IdGrupo2 left join PCGrupo3 on  PCGrupo3.IdGrupo3 = PCProvCli.IdGrupo3 \
                    inner join IVKardex on GNC.TransID = IVKardex.TransID \
                    where GNC.Estado <> 3 AND FechaTrans between  '" + fdesde + " \
                    ' and  '" + fhasta + "' and  CodTrans = '" +  obj.Transacciones +  "' \
                    group by GNC.codtrans, GNC.numtrans, GNC.NumDocRef, GNC.FechaTrans, FCVendedor.CodVendedor, \
                    PCProvCli.RUC, PCProvCli.Nombre,PCProvCli.Direccion1,PCProvCli.Telefono1, PCProvCli.Pais, \
                    PCProvCli.Ciudad,PCProvCli.Provincia,PCGrupo1.CodGrupo1, PCGrupo2.CodGrupo2 ,PCGrupo3.CodGrupo3"
                    #print(sql) ok
                    cursor.execute(sql)
                    context['datos'] = dictfetchall(cursor)
                    context['condicion']={'fdesde':fdesde,'fhasta': fhasta, 'numresultado':str(len(context['datos']))}
                    #print("datos: " + str(len(context['datos'])))

                except Exception as e:
                    context['datos'] =''
                    errors.append('error en consulta')
                    errors.append(str(e))
        else:
            errors.append('debe ingresar las dos fechas de busqueda')
    except Exception as e:
        if server:
            errors.append('no se ha podido encontrar servidor SQL server')
            errors.append(str(e))
        else:
            errors.append('no se ha configurado la base de datos')
            errors.append(str(e))
    try:

        context['configuracion_mongo']= {"numMongo": Ventas.objects.count, "maxDate": consFecha(request,1), "minDate": consFecha(request,0)}
    except Exception as e:
        context['configuracion_mongo']= {"numMongo": 0, "maxDate": 0, "minDate": 0}
        errors.append('base de ventas vacia')
        errors.append(str(e))
    return render(request,'import.html',{'datos':context['datos'],'condicion':context['condicion'],'configuracion_sql':context['configuracion_sql'],
                                         'configuracion_mongo':context['configuracion_mongo'], 'errors':errors })
    #return render(request,'import.html',{'errors':errors} )

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

#subrutina para copiar los datos a MONGODB
def guardarMongoAjax(request):
    response_dict={}
    if request.is_ajax():
        #guarda en la base de datos de  mongo DB
        #print("Llega al ajax")
        try:
            #priemro consulta si no estan ya guardados los datos
            obj=Configuracion.objects.get(0)
            if obj.IdentificadorTrans==1:
                res = Ventas.objects(Q(CodTrans =request.GET['CodTrans']) and Q(NumTrans= request.GET['NumTrans']) )
            else:
                res = Ventas.objects(Q(CodTrans =request.GET['CodTrans']) and Q(NumDocRef= request.GET['NumDocRef']) )
            if res:
                response= JsonResponse({'msg': "La transaccion ya existe" })
            else:
                obj=Ventas.objects.create(CodTrans=request.GET['CodTrans'],
                          NumTrans= request.GET['NumTrans'],
                          NumDocRef= request.GET['NumDocRef'],
                          FechaTrans =   datetime.strptime(request.GET['FechaTrans'] +' 0:00' , '%d/%m/%Y  %H:%M'),
                          Vendedor =  request.GET['Vendedor'],
                          NombreCliente =  request.GET['Nombre'],
                          Direccion =  request.GET['Direccion'],
                          Telefono =  request.GET['Telefono'],
                          Pais =  request.GET['Pais'],
                          Provincia =  request.GET['Provincia'],
                          #Canton =  request.GET['Canton'],
                          PCGrupo1 =  request.GET['CodGrupo1'],
                          PCGrupo2 =  request.GET['CodGrupo2'],
                          PCGrupo3 =  request.GET['CodGrupo3'],
                          Total =  price_convert(request.GET['Total']),
                          )
                obj.save()
                #print ("TODO OK")

                response= JsonResponse({'msg': "Se ha grabado con exito" })

            return HttpResponse(response.content)
        except Exception as e:
            #print ("ERROR:"+str(e))
            response= JsonResponse({'msg': str(e) })
            return HttpResponse(response.content)
    else:
        #print ("no entro en ajax")
        return redirect('/')

def price_convert(_price):
    import re
    return float(re.sub(r'[^0-9.]', '', _price))