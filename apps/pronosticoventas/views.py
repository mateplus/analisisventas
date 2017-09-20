from django.shortcuts import render
from datetime import date, datetime
import time
from apps.main.models import Ventas
from apps.main.models import Configuracion
from apps.main.models import PronosticoVentas
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from mongoengine.queryset.visitor import Q
import numpy as np
from decimal import *

meses=["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

import keras

import pandas as pd

#import matplotlib.pyplot as plt
#from decimal import Decimal

from bson.json_util import dumps
from django.views.generic import TemplateView


# Create your views here.
def VisualizarScoreClientes(request):
    return render (request,'scoreclientes.html')


class VisualizarRNATrain(TemplateView):
    template_name='rnatrain.html'
    def post(self,request,*args,**kwargs):
        context={}
        errors=[]
        #context=super(VisualizarRNATrain,self).get_context_data(**kwargs)
        try:
            context["configuracion"]={
                                        "numMongo": Ventas.objects.count,
                                        "maxDate": consFecha(1),
                                        "minDate": consFecha(0),
                                        "numClientes":PronosticoVentas.objects.count
                                    }
            if not PronosticoVentas.objects:
                errors.append("Todavia no ha generado un score de clientes!")
        except Exception as e:
            errors.append(str(e))
        context['errors'] = errors
        if 'btnDataSet' in request.POST:
            context=generaDataSet(context)
            #return render(request,'rnatrain.html', context)
        if 'btnEntrenar' in request.POST:
            #print ("entrenar")
             #entrenar al modelo
            EntrenamientoRNA(context)
        if 'btnEntrenarSVG' in request.POST:
            EntrenamientoSVG(context)
        return render(request,'rnatrain.html', context)

#def consFecha(self,bandMax):


def consFecha(bandMax):

    if bandMax==1:
        pipeline=[ {"$group":{ "_id":"", "res":{"$max":"$FechaTrans"}} } ]
    else:
        pipeline=[ {"$group":{ "_id":"", "res":{"$min":"$FechaTrans"}} } ]

    max= Ventas.objects.aggregate(*pipeline )
    resultado=list(max)

    return resultado[0]['res']


def VisualizarResultado(request):
    return render (request,'resultado.html')


#Consulta para calcular el SCORE del cliente
#class cons_score_cliente(TemplateView):
def cons_score_cliente(request):
    obj=Configuracion.objects.get(0)
    fdesde=time.strftime("%d/%m/%Y")
    fhasta=time.strftime("%d/%m/%Y")
    #print("Esto en score cliente!!!!!")
    #aqui coge lo del boton
    errors=[]
    context={}
    lista=[]


    if request.GET.get('fdesde'):
        fdesde =  request.GET['fdesde']
    else:
        errors.append("No se ha definido la fecha desde")

    if request.GET.get('fhasta'):
        fhasta=  request.GET['fhasta']
    else:
        errors.append("No se ha definido la fecha hasta")

    fdesde_date= datetime.strptime(fdesde, '%d/%m/%Y').date()
    fhasta_date= datetime.strptime(fhasta, '%d/%m/%Y').date()

    #consulta para SCORE cliente MONGODB
    #condicion para que suma la cantidad ,"cantidad":{"$sum":1}

    pipeline=[
        {"$group":{ "_id":{"RUC": "$RUCCliente"},"totalVentas":{"$sum":"$PTotal"},"totalUtilidad": {"$sum":{"$subtract":["$PTotal","$CTotal"]}},
                    "NumDiasMora":{"$max":"$NumDiasMora"},"Promedio":{"$avg":"$PTotal"}
        }}
    ]
    try:
        ScoreClientes = Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).aggregate(*pipeline)
        for doc in ScoreClientes:
            Id= dict(doc["_id"])
            #como se que es el ultimo cliente?
            #veamos y ordenamos  de manera desecendente por fecha
            res= Ventas.objects(RUCCliente=Id["RUC"]).order_by('-fechatrans') .first()
            #Person.objects.order_by('last_name', '-age')

            if res == None:
                nombre = "desconocido"
            else:
                nombre = res.NombreCliente
                direccion  = res.Direccion
                telefono  = res.Telefono

                #para el ejemplo he decidido usar la ciudad
                grupo=res.PCGrupo3
            lista.append ( {'RUC':Id["RUC"],
                           'Nombre': nombre,
                           'Direccion': direccion,
                           'Telefono': telefono,
                           'VentasVal': doc["totalVentas"],
                           'Ventas': 0,
                           'UtilVal':doc["totalUtilidad"],
                           'Utilidad': 0,
                           'DiasMora': doc["NumDiasMora"],
                           'Mora': 0,
                           'Grupo': grupo,
                           'Promedio': doc["Promedio"]
            })

        lista = CalculaScoreCliente(lista)
        context['scoreclientes'] = lista
        context['condicion']={'fdesde':fdesde,'fhasta': fhasta, 'numresultado':str(len(lista))}
        context['configuracion']={'PesoV':obj.PVenta,'PesoR': obj.PRentabilidad, 'PesoM':  obj.PMora }
    except Exception as e:
        errors.append(str(e))
        context['scoreclientes']= ''

    context['errors'] = errors
    #return context
    return render(request,'scoreclientes.html',context)


def CalculaScoreCliente(lista):
    obj=Configuracion.objects.get(0)
    arraynp = np.array([])
    ventasnp = np.array([])
    utilidadnp = np.array([])
    moranp = np.array([])
    scorecli= np.array([])
    salida=[]
    arraynp= convierte_arrayNP(lista,'VentasVal')
    #print(arraynp)
    ventasnp= calculaEscala(arraynp)
    #print(ventasnp)
    arraynp= convierte_arrayNP(lista,'UtilVal')
    utilidadnp= calculaEscala(arraynp)
    arraynp= convierte_arrayNP(lista,'DiasMora')
    moranp=calculaEscalaMora(arraynp)

    scorecli =  ventasnp* float(obj.PVenta) + utilidadnp*float(obj.PRentabilidad)  + moranp*float(obj.PMora)
    #sacamos los datos en el formato necesario
    for i in range(0,len(lista)-1):
        tmpdic =dict(lista[i])
        salida.append ( {'RUC':tmpdic["RUC"],
                   'Nombre': tmpdic["Nombre"],
                   'Direccion': tmpdic["Direccion"],
                   'Telefono': tmpdic["Telefono"],
                   'VentasVal': tmpdic["VentasVal"],
                   'Ventas': ventasnp[i],
                   'UtilVal':tmpdic["UtilVal"],
                   'Utilidad': utilidadnp[i],
                   'DiasMora': tmpdic["DiasMora"],
                   'Mora': moranp[i],
                   'Total': scorecli[i],
                   'Grupo':tmpdic["Grupo"],
                   'Promedio':tmpdic["Promedio"]
                   })
    return salida


#subrutina para calculo del score de los dias mora
def calculaEscalaMora(arraynp):
    obj=Configuracion.objects.get(0)
    #moranp = np.array([])
    moranp= np.zeros((arraynp.size,1 ))

    moranp = asignavalorMora(arraynp,moranp,obj.RMora10,10)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora9,9)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora8,8)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora7,7)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora6,6)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora5,5)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora4,4)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora3,3)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora2,2)
    moranp = asignavalorMora(arraynp,moranp,obj.RMora1,1)
    return moranp

def asignavalorMora(arraynp,moranp,condicion,valor):
    cond=""
    lstcond=[]
    cond = condicion
    lstcond=cond.split(":")
    indice= np.where((arraynp >= int(lstcond[0])) & (arraynp < int(lstcond[1])))
    moranp[indice] =valor
    return moranp


def convierte_arrayNP(lista,nombre):
    lst=[]
    tmpdic={}
    arraynp = np.array([])
    for i in lista:
        #transofroma en diccionario para tener un mejor acceso
        tmpdic =dict(i)
        #arraynp= np.vstack([tmpdic['VentasVal'], tmpdic['UtilVal']])
        lst.append(tmpdic[nombre])
    arraynp= np.vstack(lst)
    return arraynp

#subrutina que calcula el factor de la escala
def calculaEscala(arraynp):

    salidanp = np.array([])
    maxVenta= evaluamaximo(arraynp)
    #cambio de escala
    salidanp=  (arraynp *10)/maxVenta
    #arreglamos los valores que estaban fuera del rango
    salidanp[np.where(salidanp>10)] = 10
    return salidanp

#funcion para evaluar el maximo de un array considerando una
#desviacion estandar maxima de 600
def evaluamaximo(array):
    condicion = True
    cont =1
    cond_nummax = True
    while condicion or cond_nummax:
        condicion= (np.std(array) > 600)
        #devuelve el indice del numero mayor
        maxindice   =    np.argmax(array)
        #ahora lo eliminadmos
        array[maxindice]=0
        cont=cont+1
        cond_nummax= (cont <=50)

    max= np.max(array)
    return max

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

#------------------------------------------------------------------------------------------------------------------
#para guardar los datos que van a servir para alimentar a la RNA


def eliminarScore(request):
    PronosticoVentas.objects().delete()
    response= JsonResponse({'msg': "Se ha eliminado datos anteriores" })
    return HttpResponse(response.content)


def guardarScore(request):
    response_dict={}
    if request.is_ajax():
        #guarda en la base de datos de  mongo DB
        #print("Llega al ajax")
        try:
            cadRUC = request.GET['RUC']
            obj=PronosticoVentas.objects.create(RUC=cadRUC.strip(),
                          NombreCliente= request.GET['NombreCliente'],
                          Direccion= request.GET['Direccion'],
                          Telefono= request.GET['Telefono'],
                          ScoreClientes= price_convert(request.GET['ScoreClientes']),
                          Grupo=request.GET['Grupo'],
                          Promedio=request.GET['Promedio'],
                          )
            obj.save()
            response= JsonResponse({'msg': "Se ha grabado con exito" })
            return HttpResponse(response.content)
        except Exception as e:
            #print ("ERROR:"+str(e))
            response= JsonResponse({'msg': str(e) })
            return HttpResponse(response.content)
    else:
        return redirect('/')

def price_convert(_price):
    import re
    return float(re.sub(r'[^0-9.]', '', _price))

#------------------------------------------------------------------------------------------------------------------------
#RNA


def generaDataSet(context):
    dataset =PreProcesamientoDatos()
    dataset.to_csv('out.csv',encoding='utf-8', header=True,columns =("RUC","Grupo","Anio","Mes","Score","ItemsTotal","Promedio","cantidad","Vtotal"))
    #context={}
    errors=[]
    try:
        context["configuracion"]={
                                    "numClientes":PronosticoVentas.objects.count,
                                    "total":len(dataset.index),
                                    "totaltrain": len(dataset.index)*(8/10),
                                    "totaltest":len(dataset.index)*(2/10)
                                }

    #EntrenamientoRNA(dataset)  header=True,cols=["b","a","c"], engine='python'
    #print(dataset)
    except  Exception as e:
            errors.append(str(e))
    context['errors'] = errors
    #return HttpResponse(request)
    #return render(request,'rnatrain.html',context)
    #return HttpResponse(response.content)
    return context

#realiza las consultas necesarias y devuelve un vector tipo NP con el data set que sera apliacado a la RNA
def PreProcesamientoDatos():

    pipeline=[ {"$group":{ "_id":{"RUC":"$RUCCliente","mes":{"$month": "$FechaTrans"},"anio":{"$year": "$FechaTrans"} },
                           "VTotal":{"$sum":"$PTotal"},"ItemsTotal":{"$sum":"$ItemsTotal"},"Promedio":{"$avg":"$PTotal"},"cantidad":{"$sum":1}}}]
    data2 = PronosticoVentas.objects
    lista=[]
    for d in data2:
        data1= Ventas.objects(RUCCliente=d.RUC).aggregate(*pipeline)
        #data1_fields = ['_id','VTotal','ItemasTotal']
        #result = pd.DataFrame(list(data1), columns = data1_fields)
        for doc in data1:
            y=dict(doc["_id"])
            lista.append({ 'RUC':d.RUC,
                           'Grupo':d.Grupo,
                           'Anio':y['anio'],
                           'Mes':y['mes'],
                           'Score':d.ScoreClientes,
                           'ItemsTotal':doc["ItemsTotal"],
                           'Promedio':doc["Promedio"],
                           'cantidad':doc["cantidad"],
                           'Vtotal':doc["VTotal"],
                       })
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(lista)
    return df

#recibe el dataset y define la red neuronal la entrena y guarda el resultado
def EntrenamientoRNA(context):


    dataset = pd.read_csv('out.csv')
    X = dataset.iloc[:, 4:9].values
    y = dataset.iloc[:, 9].values

    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    onehotencoder=OneHotEncoder(categorical_features=[0])
    X=onehotencoder.fit_transform(X).toarray()
    X=X[:,1:]
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

    from sklearn.preprocessing import StandardScaler
    sc_X=StandardScaler()

    X_train_sc=sc_X.fit_transform(X_train)
    X_test_sc=sc_X.fit_transform(X_test)


    sc_Y=StandardScaler()
    #y_train_sc=sc_Y.fit_transform(y_train.reshape(1,-1))
    #print(y_train.reshape(1,-1))
    #print(y_train.reshape(-1,1))

    y_train_sc=sc_Y.fit_transform(y_train.reshape(-1,1))
    #print(y_train)
    #y_test_sc=sc_Y.fit_transform(y_test.reshape(1,-1))

    from keras.models import Sequential
    from keras.layers.core import Dense, Activation
    from keras import backend as K

    model = Sequential()
        #model.add(Dense(input_dim=16,output_dim=64, kernel_initializer='normal', init='uniform',activation=('relu')))
    model.add(Dense(input_dim=15,output_dim=64, kernel_initializer='normal',activation=('relu')))
    model.add(Dense(output_dim=64, kernel_initializer='normal', activation=('relu') ))
    model.add(Dense(output_dim=32, kernel_initializer='normal',activation=('relu') ))
    model.add(Dense(output_dim=15, kernel_initializer='normal',activation=('relu') ))
    model.add(Dense(output_dim=1, kernel_initializer='normal'))

    model.compile(loss='mean_squared_error', optimizer='adam')


    model.fit(X_train_sc, y_train_sc, batch_size=100,nb_epoch=1000)
    #from keras.models import load_model
    #model = load_model('my_model.h5')

    #print(X_test_sc)
    y_pred = sc_Y.inverse_transform(model.predict(X_test_sc))
    #y_pred = model.predict(X_test_sc)
    from sklearn.metrics import r2_score
    #r2_score(y_test, y_pred)
    model.save('my_model.h5')
    #guarda las escalas
    from sklearn.externals import joblib
    scaler_filename = "scalerX.save"
    joblib.dump(sc_X, scaler_filename)
    scaler_filename = "scalerY.save"
    joblib.dump(sc_Y, scaler_filename)

    context['RNA']={'r_cuadrado':r2_score(y_test, y_pred)}

    if K.backend() == 'tensorflow':
        K.clear_session()

    return context


def EntrenamientoSVG(context):
    import numpy as np
    import pandas as pd

    dataset = pd.read_csv('out.csv')
    X = dataset.iloc[:, 4:9].values
    y = dataset.iloc[:, 9].values
    #Codificar las variables categoricas
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    onehotencoder=OneHotEncoder(categorical_features=[0])
    X=onehotencoder.fit_transform(X).toarray()
    X=X[:,1:]

    # Splitting the dataset into the Training set and Test set
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

    #feature scaling
    from sklearn.preprocessing import StandardScaler
    sc_X=StandardScaler()
    X_train_sc=sc_X.fit_transform(X_train)
    X_test_sc=sc_X.fit_transform(X_test)

    sc_Y=StandardScaler()
    y_train_sc=sc_Y.fit_transform(y_train.reshape(-1,1))

    from sklearn.externals import joblib
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    reglin = LinearRegression()
    reglin.fit(X_train,y_train)
    joblib.dump(reglin, 'reglin.pkl')

    y_pred_linear=reglin.predict(X_test)

    #-----------------------------------------------------------------------------------------------
    from sklearn.svm import SVR

    regressor=SVR(kernel='rbf', C=200, gamma=0.001)
    regressor.fit(X_train_sc,y_train_sc)
    joblib.dump(regressor, 'svr.pkl')

    #predecir los resultados
    y_pred=sc_Y.inverse_transform(regressor.predict(X_test_sc))

    y_out=(y_pred_linear + y_pred ) /2
    context['SVR']={'r_cuadrado':r2_score(y_test, y_out)}
    print(r2_score(y_test, y_out),"Error medio cuadratico")
    scaler_filename = "scalerX_SVG.save"
    joblib.dump(sc_X, scaler_filename)
    scaler_filename = "scalerY_SVG.save"
    joblib.dump(sc_Y, scaler_filename)

    return context

class VisualizarReporte(TemplateView):


    template_name='reporte.html'
    def get_context_data(self,**kwargs):
        from datetime import datetime
        context=super(VisualizarReporte,self).get_context_data(**kwargs)
        context['meses'] = meses
        ahora = datetime.now()
        anio=ahora.year
        context['reporte'] ={"mes": int(1),"anio":anio }

        return context

#---------------------------------------------------------------------------------------------------------------------------
def consReporte(request):
    import time
    from datetime import datetime,timedelta
    from dateutil.relativedelta import relativedelta
    from keras.models import load_model

    context={}
    errors=[]
    #try:
        #data2 = PronosticoVentas.objects
        #lista=[]
    mes=request.GET['mes']
    ahora = datetime.now()
    anio=ahora.year
    #anio=2016

    'primer dia del mes'
    fdesde_date = datetime(anio,int(mes),1).date()
    month = relativedelta(months=1)
    fhasta_date= fdesde_date +month
    dias = timedelta(days=1)
    fhasta_date= fhasta_date -dias

    #consulta para SCORE cliente MONGODB
    #condicion para que suma la cantidad ,"cantidad":{"$sum":1}
    #print(fdesde_date)
    #print(fhasta_date)
    lista=[]
    #db.inventory.find( { type: 'food' }, { item: 1, qty: 1, _id:0 } )
    clientes = PronosticoVentas.objects.fields(RUC=1 , NombreCliente=1,Direccion =1,Telefono=1,ScoreClientes=1,Promedio=1).order_by('-ScoreClientes')
    bandMesconVentas = True if   Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).filter().count() > 0 else False

    #venta esperada, uso de la red neuronal
    model = load_model('my_model.h5')

    for cli in clientes:
        #aqui consultamos las ventas actuales
        #Reporte= Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).filter(RUCCliente=cli.RUC).aggregate(*pipeline)
        Vreal= Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).filter(RUCCliente=cli.RUC).sum('PTotal')
        ItemsTotal= Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).filter(RUCCliente=cli.RUC).sum('ItemsTotal')
        Cantidad= Ventas.objects(Q(FechaTrans__gte=fdesde_date) & Q(FechaTrans__lt=fhasta_date)).filter(RUCCliente=cli.RUC).count()
        Vhist=VentaHistorica(mes,cli.RUC)
        #orden de campos Mes	Score	ItemsTotal	Promedio	cantidad

        if Vreal != 0:
            promedio = float(cli.Promedio)

        else:
            promedio = float(Vhist[0])
            ItemsTotal= float(Vhist[1])
            Cantidad = float(Vhist[2])


        X = np.array([int(mes), int(cli.ScoreClientes),int(ItemsTotal) ,promedio,int(Cantidad)])
        #real=np.array(Vreal if Vreal>0 else Vhist)
        #venta_pred =CalculaVentaPred(model,X)
        venta_pred =CalculaVentaPredSVR(X)
        # la diferencia se base en el hecho de que haya ventas en el mes o no

        if bandMesconVentas == True:
            diferencia =  Decimal(venta_pred)- Decimal(Vreal)
        else:
            diferencia = Decimal(venta_pred) - Vhist[0]



        lista.append( { 'RUC': cli.RUC,
                      'Nombre':cli.NombreCliente,
                      'Direccion1':cli.Direccion,
                      'Telefono1':cli.Telefono,
                      'Score':cli.ScoreClientes,
                      'Vhist':Vhist[0],
                      'Vreal':Vreal,
                      'Vcalculada':venta_pred,
                      'Diferencia':diferencia
                      })
    context['datos'] =lista
    context['errors'] = errors
    context['meses'] = meses
    context['reporte'] ={"mes": int(mes),"anio":anio,"numresultado":str(len(context['datos'])) }




     #context['venta_resmen']= {"max": Ventas.objects.count, "maxDate": consFecha(request,1), "minDate": consFecha(request,0)}
    #print(context)

    #consutla de reporte final
    return render(request,'reporte.html',context)

#es es un numpy array
def CalculaVentaPred(model,X):
    #La comuna uno tiene el nuemro del mese
    #debemos transformarala en 11 columnas
    mes= X[0]
    Z=np.zeros((1,12),dtype=int )
    Z[0,int(mes)-1]=1
    X_test=np.append(Z,X[[1,2,3,4]])
    X_test= X_test[1:]

    from sklearn.externals import joblib
    scaler_filename = "scalerX.save"
    sc_X = joblib.load(scaler_filename)
    scaler_filename = "scalerY.save"
    sc_Y = joblib.load(scaler_filename)
    X_test= X_test.reshape(1, -1)
    X_test = X_test.astype(float)
    X_test_sc=sc_X.transform(X_test)
    #Y_test_sc=sc_Y.fit_transform(real)

    #y_pred = model.predict(X_test_sc)
    y_pred = sc_Y.inverse_transform(model.predict(X_test_sc))
    return  str(y_pred[0,0])


def CalculaVentaPredSVR(X):
    mes= X[0]
    Z=np.zeros((1,12),dtype=int )
    Z[0,int(mes)-1]=1
    X_test=np.append(Z,X[[1,2,3,4]])
    X_test= X_test[1:]

    from sklearn.externals import joblib
    scaler_filename = "scalerX_SVG.save"
    sc_X = joblib.load(scaler_filename)
    scaler_filename = "scalerY_SVG.save"
    sc_Y = joblib.load(scaler_filename)
    X_test= X_test.reshape(1, -1)
    X_test = X_test.astype(float)
    X_test_sc=sc_X.transform(X_test)
    #egresion lineal
    reglin= joblib.load('reglin.pkl')
    regressor= joblib.load('svr.pkl')
    y_pred_linear=reglin.predict(X_test)
    y_pred=sc_Y.inverse_transform(regressor.predict(X_test_sc))
    y_out=(y_pred_linear + y_pred ) /2
    print(y_out)
    return  str(y_out[0])

#primero trata de buscar un historico de las ventas del mes
#especificado promediado de todos los anios
#si no lo encuentre se conformo con un promedio mensula general


def VentaHistorica(mes,RUC):
    pipeline=[
        {"$group":{ "_id":{"RUC": "$RUCCliente", "mes":{"$month": "$FechaTrans"},"anio":{"$year": "$FechaTrans"}},"totalVentas":{"$sum":"$PTotal"},"totalItems":{"$sum":"$ItemsTotal"}, "count": {"$sum":1}
                    }
        },
       {"$group":{"_id": {"mes": "$_id.mes", "RUC":"$_id.RUC"}, "promedio" : {"$avg": "$totalVentas" }, "items" : {"$avg": "$totalItems" },"cantidad":{"$avg":"$count"} }}
    ]
    Vtas= Ventas.objects().filter(RUCCliente=RUC).aggregate(*pipeline)
    promedio = 0
    items=0
    cantidad =0
    aux=0
    totalitems=0
    cantidadtotal =0
    cnt=0
    for vmes in Vtas:
        cnt=cnt+1
        y=dict(vmes["_id"])
        #print( dumps(vmes) )
        dic= dict(vmes)

        totalitems=totalitems + float( dic["items"])
        #aux=vmes.cantidad
        cantidadtotal= cantidadtotal + float( dic["cantidad"])
        if mes==y["mes"]:
            promedio = vmes.promedio
            items = vmes.items
            cantidad = vmes.cantidad

    if promedio==0:
        #no se ha vendido nunca en el mismo mes por lo que voy a calcular un promedio total de ventas
        if cnt != 0:
            items = totalitems/cnt
            cantidad = cantidadtotal/cnt

        cursor= PronosticoVentas.objects().filter(RUC=RUC)

        for i in cursor:
            promedio=i.Promedio


    return [promedio,items,cantidad]
