from django.contrib import admin
from amministrazione.models import *

# Register your models here.
class AdminServizi(admin.ModelAdmin):
    list_display = ('codice_servizio','nome','versione_get',)
    search_fields = ('codice_servizio','nome','codice_versione',)

    def versione_get(self,obj):
        versione = ""
        for carattere in str(obj.codice_versione):
            versione += carattere+"."
        return versione
    versione_get.short_description = "Versione"

class AdminClienteAPI(admin.ModelAdmin):
    list_display = ('cognome','nome','azienda',)
    search_fields = ('cognome','nome','n_telefono','n_cellulare','email','c_fiscale','azienda',)

class AdminLicenza(admin.ModelAdmin):
    list_display = ('cliente', 'codice_licenza','data_inizio','data_fine')


admin.site.register(Servizio,AdminServizi)
admin.site.register(ClienteAPI,AdminClienteAPI)
admin.site.register(Licenza,AdminLicenza)