from django.forms import *
from archivio.models import *
from negozio.models import *
from django.contrib.admin import widgets
from dal_select2.widgets import ModelSelect2Multiple
from dal_select2.widgets import ModelSelect2


class CopiaProdottiForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    stampante = CharField(label="Inserisci ID della stampante da dove vuoi copiare i prodotti ")

class CambiaCategoriaStampanteForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    categoria = ModelChoiceField(queryset=Categoria.objects.all(),label="Seleziona la categoria da impostare come nuova")

class CambiaSerieStampanteForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)

    serie = ModelChoiceField(queryset=Serie.objects.all().order_by("nome"),
                     label="Seleziona la serie da impostare come nuova")

    def __init__(self,*args,**kwargs):
        current_marca = None
        try:
            current_marca = kwargs.pop("marca")
        except:
            pass

        super(CambiaSerieStampanteForm, self).__init__(*args, **kwargs)

        if current_marca is not None:
            self.fields["serie"] = ModelChoiceField(queryset=Serie.objects.filter(marca=current_marca).order_by("nome"),
                                                             label="Seleziona la serie da impostare come nuova")
        else:
            self.fields["serie"] = ModelChoiceField(queryset=Serie.objects.all().order_by("nome"),
                             label="Seleziona la serie da impostare come nuova")

class CambiaMarcaStampanteForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    marca = ModelChoiceField(queryset=Produttore.objects.all(),label="Seleziona la marca da impostare come nuova")

class CambiaMarcaProdottoForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    marca = ModelChoiceField(queryset=Produttore.objects.all(),label="Seleziona la marca da impostare come nuova")

class CambiaCategoriaProdottoForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    categoria = ModelChoiceField(queryset=Categoria.objects.all(),label="Seleziona la categoria da impostare come nuova")

class CambiaColoreProdottoForm(forms.Form):
    _selected_action = CharField(widget=MultipleHiddenInput)
    colore = ModelChoiceField(queryset=Colore.objects.all(),label="Seleziona il colore da impostare come nuovo")

class SerieForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SerieForm, self).__init__(*args, **kwargs)
        self.fields["marca"].queryset = Produttore.objects.all().order_by("nome")

    class Meta:
        model = Serie
        exclude = ('has_prodotti',)
        widgets = {
            'marca': ModelSelect2(url='produttore-autocomplete')
        }


class StampanteForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(StampanteForm, self).__init__(*args, **kwargs)
        self.fields["marca"].queryset = Produttore.objects.all().order_by("nome")
        self.fields["serie"].queryset = Serie.objects.all().order_by("nome")


    class Meta:
        model = Stampante
        exclude = ('has_prodotti',)
        widgets = {
            'prodotti_associati' : ModelSelect2Multiple(url='prodotto-autocomplete'),
            'marca': ModelSelect2(url='produttore-autocomplete'),
            'categoria':ModelSelect2(url='categoria-autocomplete'),
            'serie': ModelSelect2(url='serie-autocomplete')
        }

class ProdottoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProdottoForm, self).__init__(*args, **kwargs)

        if "instance" in kwargs:
            obj = kwargs.pop("instance")
            if obj is not None:
                self.fields["offerte"].queryset = Offerte.objects.all().filter(mpn=obj.mpn)
        else:
            self.fields["offerte"].queryset = Offerte.objects.none()
        self.fields["marca"].queryset = Produttore.objects.all().order_by("nome")


    class Meta:
        model = Prodotto
        exclude = ('has_prodotti',)
        widgets = {
            'marca': ModelSelect2(url='produttore-autocomplete'),
            'categoria': ModelSelect2(url='categoria-autocomplete'),
        }



