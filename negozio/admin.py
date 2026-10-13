from django.contrib import admin
from negozio.forms import *
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.http.response import HttpResponse
from django.db.models import Q
import csv
from decimal import Decimal


class ConfigurazioneAdmin(admin.ModelAdmin):
    list_display = ('nome','valore')
    search_fields = ('nome','valore')

class SliderChildrenAdmin(admin.ModelAdmin):
    list_display = ('titolo',)
    search_fields = ('titolo','url',)

class SliderAdmin(admin.ModelAdmin):
    list_display = ('nome','n_slides','attivo')
    search_fields = ('nome', )
    filter_horizontal = ('slides',)

    def n_slides(self,obj):
        return obj.slides.all().count()
    n_slides.short_description = "N. Immagini"

class PaginaAdmin(admin.ModelAdmin):
    list_display = ('titolo',"posizione",'pubblicata','url')
    prepopulated_fields = {'slug':('titolo',)}


def elimina_selezionati(modeladmin, request, queryset):
    for obj in queryset:
        try:
            os.remove(obj.file_listino.path)
        except:
            pass
        obj.delete()

class AdminListino(admin.ModelAdmin):
    list_display = ('id','data_upload','nome_file','righe_lette','righe_elaborate','offerte_aggiunte','offerte_eliminate','action')
    list_display_links = None
    actions = [elimina_selezionati]

    def get_actions(self, request):
        actions = super(AdminListino, self).get_actions(request)
        del actions['delete_selected']
        return actions

    fieldsets = (
        ('Listino', {
            'fields': ('file_listino',)
        }),
    )

    elimina_selezionati.short_description = "Elimina listini selezionati"


    def action(self,obj):

        if obj.righe_lette == obj.righe_elaborate:
            return "Listino elaborato"
        elif obj.righe_elaborate > 0:
            return "In elaborazione"
        elif obj.righe_elaborate == 0:
            return mark_safe("<a href='elabora/{id}' id='elabora' target='_blank'>Elabora listino</a>".format(id=obj.id))
    action.short_description = "STATO"


    def get_urls(self):
        urls = super(AdminListino, self).get_urls()
        my_urls = [
            url(r'^elabora/(?P<id>[\d]+)/$', self.admin_site.admin_view(self.elabora_listino)),
        ]
        return my_urls + urls


    def elabora_listino(self,request,id):
        listino = Listino.objects.get(id=id)

        righe_elaborate = listino.righe_elaborate

        with open(listino.file_listino.name, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='.')
            spamreader = list(spamreader)

            if righe_elaborate == 0:
                Offerte.objects.all().update(attiva=0,aggiornata=False)
            else:
                spamreader= spamreader[righe_elaborate:]

            for row in spamreader:

                mpn = str(row[0]).replace('"', "")
                ean = row[1]
                fornitore = str(row[4]).replace('"', "")

                prodotti = Prodotto.objects.filter(Q(mpn=mpn) | Q(ean=ean))

                if prodotti.count() != 0:

                    cerca_offerta = Offerte.objects.all().filter(mpn=mpn, ean=ean,
                                                                 prezzo=Decimal(str(row[2]).replace(",", ".")),
                                                                 qta=int(row[3]),fornitore=fornitore)
                    offerta = Offerte()
                    if cerca_offerta.count() == 0:
                        cerca_esistente = Offerte.objects.all().filter(mpn=mpn, ean=ean)
                        if cerca_esistente.count() != 0:
                            offerta = cerca_esistente[0]
                            offerta.aggiornata = True
                            offerta.mpn = mpn
                            offerta.ean = ean
                            offerta.attiva = 1
                            offerta.prezzo = Decimal(str(row[2]).replace(",", "."))
                            offerta.prezzo_ivato = Decimal(float(offerta.prezzo) + float(offerta.prezzo) * 0.22)
                            offerta.qta = int(row[3])
                            offerta.fornitore = fornitore
                            offerta.save()
                            prodotti[0].offerte.filter(mpn=mpn).all().delete()
                            prodotti[0].offerte.add(offerta)
                            prodotti[0].save()
                        else:
                            offerta = Offerte()
                            offerta.data_creazione = datetime.datetime.now()
                            offerta.aggiornata = True
                            offerta.mpn = mpn
                            offerta.ean = ean
                            offerta.attiva = 1
                            offerta.prezzo = Decimal(str(row[2]).replace(",", "."))
                            offerta.prezzo_ivato = Decimal(float(offerta.prezzo) + float(offerta.prezzo)*0.22)
                            offerta.qta = int(row[3])
                            offerta.fornitore = fornitore
                            offerta.save()
                            listino.offerte_aggiunte = listino.offerte_aggiunte + 1
                            prodotti[0].offerte.filter(mpn=mpn).all().delete()
                            prodotti[0].offerte.add(offerta)
                            prodotti[0].save()
                    else:
                        offerta = cerca_offerta[0]
                        offerta.attiva = 1
                        offerta.save()


                righe_elaborate = righe_elaborate + 1
                listino.righe_elaborate = righe_elaborate
                listino.save()

        if listino.righe_lette == listino.righe_elaborate:
            listino.offerte_eliminate = Offerte.objects.filter(attiva=0).all().count()
            listino.save()
            Offerte.objects.filter(attiva=0).all().delete()


        return HttpResponse("Listino elaborato")

    def nome_file(self,obj):
        return os.path.basename(obj.file_listino.name)

class AdminOfferte(admin.ModelAdmin):
    list_display = ('mpn', 'ean', 'qta', 'get_prezzo','get_prezzo_iva','fornitore')
    search_fields = ('mpn','ean')
    list_filter = ('attiva','fornitore')

    fieldsets = (
        ('Informazioni base', {
            'fields': ('mpn', 'ean', 'qta', 'prezzo','attiva','fornitore',)
        }),
    )

    def get_prezzo(self, obj):
        return mark_safe("{prezzo} &euro;".format(prezzo=obj.prezzo))
    get_prezzo.short_description = "Prezzo"

    def get_prezzo_iva(self, obj):
        return mark_safe("{prezzo} &euro;".format(prezzo=obj.prezzo_ivato))

    get_prezzo_iva.short_description = "Prezzo (iva inclusa)"

class AdminFasciaPrezzo(admin.ModelAdmin):
    list_display = ('get_prezzo_minimo','get_prezzo_massimo','get_costo')

    def get_prezzo_minimo(self, obj):
        return mark_safe("{prezzo} &euro;".format(prezzo=obj.prezzo_minimo))
    get_prezzo_minimo.short_description = "Prezzo minimo"

    def get_prezzo_massimo(self, obj):
        return mark_safe("{prezzo} &euro;".format(prezzo=obj.prezzo_massimo))
    get_prezzo_massimo.short_description = "Prezzo massimo"

    def get_costo(self, obj):
        return mark_safe("{prezzo} &euro;".format(prezzo=obj.costo))
    get_costo.short_description = "Costo"

class AdminCorriere(admin.ModelAdmin):
    list_display = ('nome','get_logo','attivo',)
    search_fields = ('nome',)
    filter_horizontal = ('fasce_prezzo',)

    def get_logo(self, obj):
        if obj.logo.name != "":
            return mark_safe("<img width='80px' height='auto' src='/assets/carrier/{image}'".format(
                image=os.path.basename(obj.logo.name)))
    get_logo.short_description = "Logo"

class AdminCliente(admin.ModelAdmin):
    list_display = ('username','nome','cognome',)


class AdminIndirizzo(admin.ModelAdmin):
    form = IndirizzoForm
    list_display = ('alias','utente','via','citta','n_civico')



class InlineRigaOrdine(admin.TabularInline):
    model = RigaOrdine
    form = RigaOrdineForm
    extra = 1

def segna_come_pagato(modeladmin,request,queryset):

    for ordine in queryset:
        ordine.stato_id = 8
        ordine.save()
        try:
            ordine.invia_email_pagato()
        except:
            pass
def segna_come_spedito(modeladmin,request,queryset):

    for ordine in queryset:
        ordine.stato_id = 4
        ordine.save()
        try:
            ordine.invia_email_spedito()
        except:
            pass
class AdminOrdine(admin.ModelAdmin):
    list_display = ('codice','data','cliente','stato','spese_spedizione','totale_prodotti','totale_da_pagare')
    inlines = [
        InlineRigaOrdine
    ]
    form = OrdineForm
    actions = [segna_come_pagato,segna_come_spedito]

class AdminRigaOrdine(admin.ModelAdmin):
    form = RigaOrdineForm

class AdminStampantePreferita(admin.ModelAdmin):
    list_display = ('cliente','n_stampanti')
    form = StampantePreferitaForm

    def n_stampanti(self,obj):
        return obj.stampante.all().count()


# Register your models here.
admin.site.register(Configurazione,ConfigurazioneAdmin)
admin.site.register(SliderChildren,SliderChildrenAdmin)
admin.site.register(Slider,SliderAdmin)
admin.site.register(Pagina,PaginaAdmin)
admin.site.register(Listino,AdminListino)
admin.site.register(Offerte,AdminOfferte)
admin.site.register(FasciaCorriere,AdminFasciaPrezzo)
admin.site.register(Corriere,AdminCorriere)
admin.site.register(Cliente,AdminCliente)
admin.site.register(Indirizzo,AdminIndirizzo)
admin.site.register(StatoOrdine)
admin.site.register(Pagamento)
admin.site.register(Ordine,AdminOrdine)
admin.site.register(StampantePreferita,AdminStampantePreferita)