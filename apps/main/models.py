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
    IdentificadorTrans = IntField()
    #1 es numtrans  2 es numdocref

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
    NombreCliente= StringField(max_length=150)
    Direccion= StringField(max_length=150)
    Telefono= StringField(max_length=25)
    Pais= StringField(max_length=25)
    Provincia= StringField(max_length=25)
    #Canton= StringField(max_length=25)
    PCGrupo1 = StringField(max_length=25)
    PCGrupo2 = StringField(max_length=25)
    PCGrupo3 = StringField(max_length=25)
    Total = DecimalField ()

