from __future__ import unicode_literals
from mongoengine import *
from django.db import models
#from djangotoolbox.fields import EmbeddedModelField


class Configuracion(Document):
    samiServer= StringField(max_length=120)
    usuarioSQL= StringField(max_length=120)
    passSQL= StringField(max_length=120)
    Transacciones= StringField(max_length=120)
    baseDatosSQL= StringField(max_length=120)

    #1 es numtrans  2 es numdocref
    IdentificadorTrans = IntField()
    #campos para calcular el SCORE del Cliente PesoVenta, PesoRentabilidad, PesoMora
    PVenta = DecimalField()
    PRentabilidad = DecimalField()
    PMora = DecimalField()
    #campos para comparacion de dias mora
    RMora10= StringField(max_length=15)
    RMora9= StringField(max_length=15)
    RMora8= StringField(max_length=15)
    RMora7= StringField(max_length=15)
    RMora6= StringField(max_length=15)
    RMora5= StringField(max_length=15)
    RMora4= StringField(max_length=15)
    RMora3= StringField(max_length=15)
    RMora2= StringField(max_length=15)
    RMora1= StringField(max_length=15)

    def __unicode__(self):
            return self.samiServer
    @property
    def slug(self):
        return self.samiServer.replace(" ", "_")

class Detalle(EmbeddedDocument):
    CodInventario = StringField(max_length=25)
    Descripcion = StringField(max_length=120)
    Cantidad = DecimalField ()
    PU =DecimalField ()
    PT = DecimalField ()
    IVGrupo1 = StringField(max_length=25)
    IVGrupo2 = StringField(max_length=25)

class Ventas(Document):
    created_on=DateTimeField()
    detalles = ListField(EmbeddedDocumentField('Detalle'))
    #detalle = EmbeddedModelField('Detalle')
    FechaTrans = DateTimeField()
    CodTrans = StringField(max_length=10)
    NumTrans = IntField()
    NumDocRef = StringField(max_length=20)
    BaseOrigen=StringField(max_length=20)
    Vendedor=StringField(max_length=120)
    RUCCliente=StringField(max_length=13)
    NombreCliente= StringField(max_length=150)
    Direccion= StringField(max_length=150)
    Telefono= StringField(max_length=25)
    Pais= StringField(max_length=25)
    Provincia= StringField(max_length=25)
    #Canton= StringField(max_length=25)
    PCGrupo1 = StringField(max_length=25)
    PCGrupo2 = StringField(max_length=25)
    PCGrupo3 = StringField(max_length=25)
    PTotal = DecimalField ()
    CTotal = DecimalField ()
    NumDiasMora =IntField()
    ItemsTotal =   DecimalField ()

#datos para alimentar a la RNA
class PronosticoVentas(Document):
    RUC =StringField(max_length=13)
    NombreCliente= StringField(max_length=150)
    Direccion= StringField(max_length=150)
    Telefono= StringField(max_length=25)
    #NumProductos=IntField()
    #NumMes=IntField()
    ScoreClientes=IntField()
    Grupo = StringField(max_length=25)
    Promedio = DecimalField ()
    #Venta = DecimalField ()
    def save(self, *args, **kwargs):
        if not self.Grupo:
            self.Grupo = 'Desconocido'
        return super(PronosticoVentas, self).save(*args, **kwargs)