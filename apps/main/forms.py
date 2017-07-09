from django import forms
from .models import Configuracion

class ConfigForm(forms.ModelForm):

	class Meta:
		model= Configuracion
