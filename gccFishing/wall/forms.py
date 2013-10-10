from django import forms
from django.forms import ModelForm 
from models import Wallpost


class Wallpostform(ModelForm):


	text = forms.CharField(required= False)
	image = forms.ImageField(required = False)
	fields = ('text', 'image')

	class Meta:	

		model = Wallpost
