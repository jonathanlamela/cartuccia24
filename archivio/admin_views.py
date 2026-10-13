from django.http import HttpResponseRedirect
from django.shortcuts import render
from archivio.forms import *
from dal import autocomplete
from archivio.models import *
from django.db.models import Q
from dal_select2.views import Select2QuerySetView
import copy

def copia_modello(modeladmin,request,queryset):
    obj = Stampante.objects.get(pk=queryset[0].pk)

    copia = obj
    copia.pk = None
    copia.mpn = copia.mpn + "#COPIA"
    copia.save()

    for prodotto in Stampante.objects.get(pk=queryset[0].pk).prodotti_associati.all():
        copia.prodotti_associati.add(prodotto)

def copia_prodotto(modeladmin, request, queryset):
    obj = Prodotto.objects.get(pk=queryset[0].pk)

    copia = obj
    copia.pk = None
    copia.mpn = copia.mpn + "#COPIA"
    copia.save()


def attiva_stampanti_selezionate(modeladmin, request, queryset):
    queryset.update(attivo=True)

def disattiva_stampanti_selezionate(modeladmin, request, queryset):
    queryset.update(attivo=False)

def attiva_prodotti_selezionati(modeladmin, request, queryset):
    queryset.update(attivo=True)

def disattiva_prodotti_selezionati(modeladmin, request, queryset):
    queryset.update(attivo=False)

def cambia_marca_stampante(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CambiaMarcaStampanteForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['marca']

            msg = ""
            msg = "Cambio marca completato con successo"

            queryset.update(marca=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)

        form = CambiaMarcaStampanteForm(
            initial={'_selected_action': selected})

    return render(request, 'admin/cambia_marca_stampante.html', {'modelli': queryset,
                                                                 'marca_form': form,
                                                                 })

def cambia_marca_prodotto(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CambiaMarcaProdottoForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['marca']

            msg = ""
            msg = "Cambio marca completato con successo"

            queryset.update(marca=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)

        form = CambiaMarcaProdottoForm(
            initial={'_selected_action': selected})

    return render(request, 'admin/cambia_marca_prodotto.html', {'modelli': queryset,
                                                                 'marca_form': form,
                                                                 })

def cambia_categoria_prodotto(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CambiaCategoriaProdottoForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['categoria']

            msg = ""
            msg = "Cambio categoria completato con successo"

            queryset.update(categoria=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)

        form = CambiaCategoriaStampanteForm(initial={'_selected_action': selected})

    return render(request, 'admin/cambia_categoria_prodotto.html', {'modelli': queryset,
                                                         'categorie_form': form,
                                                         })

def cambia_serie_stampante(self,request,queryset):
    form = None
    if 'apply' in request.POST:
        form = CambiaSerieStampanteForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['serie']

            msg = ""
            msg = "Cambio serie completato con successo"

            queryset.update(serie=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:

        selected = list()

        for item in queryset:
            selected.append(item.id)

        if "marca" in request.GET:
            form = CambiaSerieStampanteForm(
            initial={'_selected_action': selected},marca=request.GET["marca"])
        else:
            form = CambiaSerieStampanteForm(
                initial={'_selected_action': selected},
                marca=None)


    return render(request, 'admin/cambia_serie_stampante.html', {'modelli': queryset,
                                                                     'serie_form': form,
                                                                     })

def cambia_categoria_stampante(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CambiaCategoriaStampanteForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['categoria']

            msg = ""
            msg = "Cambio categoria completato con successo"

            queryset.update(categoria=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)

        form = CambiaCategoriaStampanteForm(initial={'_selected_action': selected})

    return render(request, 'admin/cambia_categoria_stampante.html', {'modelli': queryset,
                                                         'categorie_form': form,
                                                         })

def cambia_colore_prodotto(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CambiaColoreProdottoForm(request.POST)

        if form.is_valid():
            obj = form.cleaned_data['colore']

            msg = ""
            msg = "Cambio colore completato con successo"

            queryset.update(colore=obj)

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)


        form = CambiaColoreProdottoForm(initial={'_selected_action': selected})

    return render(request, 'admin/cambia_colore_prodotto.html', {'modelli': queryset,
                                                         'colori_form': form,
                                                         })

def copia_prodotti_da_stampante(self,request,queryset):
    form = None

    if 'apply' in request.POST:
        form = CopiaProdottiForm(request.POST)

        if form.is_valid():
            stampante = form.cleaned_data['stampante']

            msg = ""

            obj = Stampante.objects.get(pk=stampante)
            if obj is not None:
                for pr in queryset:
                    pr.prodotti_associati = obj.prodotti_associati.all()
                msg = "Associazione completata con successo"
            else:
                msg = "ID stampante non valido"

            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        selected = list()

        for item in queryset:
            selected.append(item.id)

        form = CopiaProdottiForm(initial={'_selected_action': selected})

    return render(request,'admin/copia_prodotti.html', {'modelli': queryset,
                                                             'prodotti_form': form,
                                                             })


# Create your views here.
class ProdottoAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Prodotto.objects.none()

        qs = Prodotto.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(Q(nome__icontains=self.q.encode("utf8")) | Q(mpn__icontains=self.q.encode("utf8")) | Q(ean__icontains=self.q.encode("utf8")))

        return qs.order_by("nome")

class ProduttoreAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Produttore.objects.none()

        qs = Produttore.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(nome__icontains=self.q.encode("utf8"))

        return qs.order_by("nome")

class SerieAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Serie.objects.none()

        qs = Serie.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(nome__icontains=self.q.encode("utf8"))

        return qs.order_by("nome")

class CategoriaAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Categoria.objects.none()

        qs = Categoria.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(nome__icontains=self.q.encode("utf8"))

        return qs.order_by("nome")





