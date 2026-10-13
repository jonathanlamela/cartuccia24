from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from salmonella.admin import SalmonellaMixin
from cartuccia24 import settings
from archivio.admin_views import *
from django.conf.urls import url
import os




# Register your models here.
class AdminCategoria(admin.ModelAdmin):
    list_display = ('id','nome','tree','icecat_id','n_prodotti_e_modelli')
    ordering = ('id','level')
    search_fields = ('id','nome','tree','icecat_id')
    list_filter = ('parent',)
    list_max_show_all = 500


    def n_prodotti_e_modelli(self, obj):
        return Prodotto.objects.filter(categoria=obj).count() + Stampante.objects.filter(categoria=obj).count()

    def tree(self,obj):
        nome = ""
        parent = obj.parent

        if parent is None:
            nome = "Root"
        else:
            while parent is not None:
                nome = parent.nome + " > " + nome
                parent = parent.parent
                if parent is None:
                    nome += obj.nome
        return nome

class AdminProduttore(admin.ModelAdmin):
    list_display = ('id','get_image','nome','icecat_id','get_slug','numero_stampanti','numero_prodotti')
    ordering = ('id',)
    search_fields = ('id','nome','icecat_id')
    list_max_show_all = 500
    list_display_links = ('id','get_image','nome')

    def get_image(self,obj):
        if obj.image.name != "":
            return mark_safe("<img width='80px' height='auto' src='/assets/manufacturer/{image}'".format(image=os.path.basename(obj.image.name)))
    get_image.short_description = "Logo"

    def numero_stampanti(self,obj):
        return mark_safe("<a href='/admin/archivio/stampante/?marca={marca}'>{numero}</a>".format(marca=obj.id,numero=Stampante.objects.all().filter(marca=obj).count()))

    def numero_prodotti(self, obj):
        return mark_safe("<a href='/admin/archivio/prodotto/?marca={marca}'>{numero}</a>".format(marca=obj.id,
                                                                                                  numero=Prodotto.objects.all().filter(
                                                                                                      marca=obj).count()))

    def get_slug(self,obj):
        if obj.slug == "":
            obj.slug = slugify(obj.nome)
            obj.save()
        return obj.slug
    get_slug.short_description = "SEO Name"

class AdminSerie(admin.ModelAdmin):
    list_display = ('id', 'nome','marca','modelli_serie')
    ordering = ('nome',)
    search_fields = ('id', 'nome','marca__nome')
    list_max_show_all = 500
    form = SerieForm

    def modelli_serie(self,obj):
        return Stampante.objects.filter(serie=obj).count()

class AdminProdottoFilter(admin.SimpleListFilter):
    title = 'stampanti associate'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'stampante'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        return Stampante.objects.get(self.value()).prodotti_associati.all()

class AdminSerieStampanteFilter(admin.SimpleListFilter):
    title = 'serie'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'serie'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        options = list()

        for pr in Serie.objects.order_by("nome"):
            options.append((pr.pk, pr.marca.nome +" "+ pr.nome+" ("+str(Stampante.objects.filter(serie=pr).count())+")"))

        return tuple(options)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value():
            return queryset.filter(serie__id=self.value())
        else:
            return queryset.all()

class AdminMarcaStampanteFilter(admin.SimpleListFilter):
    title = 'marca'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'marca'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        options = list()

        for pr in Produttore.objects.order_by("nome"):
            options.append((pr.pk, pr.nome+" ("+str(Stampante.objects.filter(marca=pr).count())+")"))

        return tuple(options)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value():
            return queryset.filter(marca__id=self.value())
        else:
            return queryset.all()

class AdminMarcaProdottoFilter(admin.SimpleListFilter):
    title = 'marca'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'marca'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        options = list()

        for pr in Produttore.objects.order_by("nome"):
            options.append((pr.pk, pr.nome + " (" + str(Prodotto.objects.filter(marca=pr).count()) + ")"))

        return tuple(options)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        if self.value():
            return queryset.filter(marca__id=self.value())
        else:
            return queryset.all()



class AdminStampanteFilter(admin.SimpleListFilter):
    title = 'numero prodotti'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'numero'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('0', 'Senza prodotti'),
            ('Almeno', 'Almeno un prodotto'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        Stampante.objects.filter()

        if self.value() == '0':
            return queryset.filter(prodotti_associati=None)
        if self.value() == 'Almeno':
            return queryset.exclude(prodotti_associati=None)


class AdminStampante(SalmonellaMixin,admin.ModelAdmin):
    list_display = ('attivo','has_prodotti','id','img', 'nome_edit', 'mpn_edit','ean_edit','serie','marca','categoria_get','n_prodotti',)
    ordering = ('nome',)
    search_fields = ('id', 'nome','mpn','ean','marca__nome','serie__nome','descrizione_lunga','descrizione_breve')
    list_display_links = ('id','img',)
    list_filter = ('attivo',AdminMarcaStampanteFilter,'categoria',AdminSerieStampanteFilter,AdminStampanteFilter,)
    actions = [copia_modello,attiva_stampanti_selezionate,disattiva_stampanti_selezionate,cambia_categoria_stampante,cambia_marca_stampante,cambia_serie_stampante,copia_prodotti_da_stampante]

    list_per_page = 500
    list_max_show_all = 500
    form = StampanteForm

    fieldsets = (
        ('Prodotti', {
            'fields': ('prodotti_associati',)
        }),
        ('Informazioni base', {
            'fields': ('nome','mpn','ean','marca','categoria','serie')
        }),
        ('Informazioni aggiuntive', {
            'fields': ('descrizione_breve', 'descrizione_lunga','url_image')
        }),
        ('Stato', {
            'fields': ('attivo',)
        }),
        ('SEO (non toccare)', {
            'fields': ('slug',)
        }),
        ('Ricerca schede e informazioni', {
            'fields': ('icecat_id',)
        }),
        ('Statistiche', {
            'fields': ('date_add','date_upd',)
        }),
    )

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """

        from django.contrib.admin.utils import lookup_needs_distinct

        import operator

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        use_distinct = False
        search_fields = self.get_search_fields(request)
        if search_fields and search_term:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in search_fields]
            or_queries = [models.Q(**{orm_lookup: search_term})
                          for orm_lookup in orm_lookups]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

            if not use_distinct:
                for search_spec in orm_lookups:
                    if lookup_needs_distinct(self.opts, search_spec):
                        use_distinct = True
                        break

        return queryset, use_distinct


    def nome_edit(self,obj):


        return mark_safe("<input style='width:100%' type='text' name='{id}' value='{name}' id='stampante_name_field'/>".format(id=obj.id,name=obj.nome.encode("ascii")))
    nome_edit.short_description = "Nome"
    nome_edit.admin_order_field = "nome"

    def categoria_get(self, obj):
        return obj.categoria.nome
    categoria_get.short_description = "CATEGORIA"

    def mpn_edit(self, obj):
        return mark_safe("<input  type='text' name='{id}' value='{name}' id='stampante_mpn_field'/>".format(id=obj.id, name=obj.mpn))
    mpn_edit.short_description = "MPN"
    mpn_edit.admin_order_field = "mpn"

    def ean_edit(self, obj):
        return mark_safe(
            "<input  type='text' name='{id}' value='{name}' id='stampante_ean_field'/>".format(id=obj.id, name=obj.ean))
    ean_edit.short_description = "EAN13"
    ean_edit.admin_order_field = "ean"

    def img(self, obj):
        if obj.url_image != "":
            return mark_safe("<img style='width:50px;height:50px;' src='{url}'/>".format(
                url=obj.url_image))
        else:
            return mark_safe("<img style='width:50px;height:50px;' src='{url}'/>".format(
                url="/images/{mpn}".format(mpn=obj.mpn)))

    img.short_description = "IMMAGINE"

    def has_prodotti(self,obj):
        if obj.prodotti_associati.count() == 0:
            return mark_safe("<img src='{static}admin/img/icon-no.svg'/>".format(static=settings.STATIC_URL))
        else:
            return mark_safe("<img src='{static}admin/img/icon-yes.svg'/>".format(static=settings.STATIC_URL))
    has_prodotti.short_description = "PRODOTTI"

    def n_prodotti(self,obj):
        if obj.slug == "":
            obj.slug = slugify(obj.nome)
            obj.save()
        return mark_safe("<a href='/admin/archivio/prodotto/?stampante__exact={stampante}'>{conteggio}</a>".format(
            conteggio=obj.prodotti_associati.all().count(), stampante=obj.id))

    def marca_nome(self,obj):
        return obj.marca.nome.encode("utf8")

    def get_urls(self):
        urls = super(AdminStampante, self).get_urls()
        my_urls = [
                   url(r'ajax/edit/$', self.admin_site.admin_view(self.ajax_edit)),
                ]
        return my_urls + urls

    def ajax_edit(self, request):

        id = request.GET["id"]
        value = request.GET["value"]
        campo = request.GET["campo"]

        obj = Stampante.objects.get(pk=id)

        if campo == "Nome":
            obj.nome = value

        if campo == "MPN":
            obj.mpn = value

        if campo == "EAN":
            obj.ean = value

        obj.save()
        return HttpResponse(
            content="Campo {campo} per il modello {id} modificato con successo.".format(campo=campo, id=id))

    marca_nome.short_description = "Marca"

class AdminColore(admin.ModelAdmin):
    list_display = ("nome","sample",'n_prodotti')
    list_max_show_all = 500

    def sample(self,obj):
        return mark_safe("<div style='width:100px;height:20px;background-color:{colore}'></div>".format(colore=obj.codice_html))
    sample.short_description = "Campione"

    def n_prodotti(self, obj):
        return Prodotto.objects.all().filter(colore=obj).count()

class AdminProdotto(admin.ModelAdmin):
    list_display = ('attivo','id','img','nome_edit', 'mpn_edit', 'ean_edit', 'marca', 'categoria_get', 'n_stampanti','colore_sample')
    ordering = ('nome',)
    search_fields = ('id', 'nome', 'mpn', 'ean', 'marca__nome','descrizione_lunga', 'descrizione_breve')
    list_filter = ('attivo',AdminMarcaProdottoFilter, 'categoria')
    actions = [copia_prodotto,attiva_prodotti_selezionati,disattiva_prodotti_selezionati,cambia_categoria_prodotto,cambia_marca_prodotto,cambia_colore_prodotto,]
    list_display_links = ('id','img', )
    list_per_page = 500
    list_max_show_all = 500
    form = ProdottoForm
    filter_horizontal = ('offerte',)


    fieldsets = (
        ('Informazioni base', {
            'fields': ('nome', 'mpn', 'ean', 'marca', 'categoria','colore',)
        }),
        ('Informazioni aggiuntive', {
            'fields': ('descrizione_breve', 'descrizione_lunga', 'url_image')
        }),
        ('Stato', {
            'fields': ('attivo',)
        }),
        ('SEO (non toccare)', {
            'fields': ('slug',)
        }),
        ('Ricerca schede e informazioni', {
            'fields': ('icecat_id',)
        }),
        ('Statistiche', {
            'fields': ('date_add', 'date_upd',)
        }),
        ('Offerte', {
            'fields': ('offerte',)
        }),
    )

    def colore_sample(self,obj):
        return mark_safe("<div style='width:100px;height:20px;background-color:{colore}'></div>".format(colore=obj.colore.codice_html))
    colore_sample.short_description = "COLORE"

    def categoria_get(self,obj):
        return obj.categoria.nome
    categoria_get.short_description = "CATEGORIA"

    def img(self, obj):
        if obj.url_image != "":
            return mark_safe("<img style='width:50px;height:50px;' src='{url}'/>".format(
            url=obj.url_image))
        else:
            return mark_safe("<img style='width:50px;height:50px;' src='{url}'/>".format(
                url="/images/{mpn}".format(mpn=obj.mpn)))
    img.short_description = "IMMAGINE"

    def n_stampanti(self, obj):
        if obj.slug == "":
            obj.slug = slugify(str(obj.id)+obj.nome)
            obj.save()
        return mark_safe("<a href='/admin/archivio/stampante/?prodotti_associati__in={prodotto}'>{conteggio}</a>".format(conteggio=Stampante.objects.filter(prodotti_associati__in=[obj,]).count(),prodotto=obj.id))
    n_stampanti.short_description = "STAMPANTI"


    def nome_edit(self, obj):

        return mark_safe("<input style='width:100%' type='text' name='{id}' value='{name}' id='prodotto_name_field'/>".format(id=obj.id,
                                                                                                            name=obj.nome.encode("utf8")))

    nome_edit.short_description = "Nome"
    nome_edit.admin_order_field = "nome"

    def mpn_edit(self, obj):
        return mark_safe(
            "<input  type='text' name='{id}' value='{name}' id='prodotto_mpn_field'/>".format(id=obj.id, name=obj.mpn))

    mpn_edit.short_description = "MPN"
    mpn_edit.admin_order_field = "mpn"

    def ean_edit(self, obj):
        return mark_safe(
            "<input  type='text' name='{id}' value='{name}' id='prodotto_ean_field'/>".format(id=obj.id, name=obj.ean))

    ean_edit.short_description = "EAN13"
    ean_edit.admin_order_field = "ean"


    def get_urls(self):
        urls = super(AdminProdotto, self).get_urls()
        my_urls = [
            url(r'ajax/edit/$', self.admin_site.admin_view(self.ajax_edit)),
        ]
        return my_urls + urls

    def ajax_edit(self, request):

        id = request.GET["id"]
        value = request.GET["value"]
        campo = request.GET["campo"]

        obj = Prodotto.objects.get(pk=id)

        if campo == "Nome":
            obj.nome = value

        if campo == "MPN":
            obj.mpn = value

        if campo == "EAN":
            obj.ean = value

        obj.save()
        return HttpResponse(content="Campo {campo} per il prodotto {id} modificato con successo.".format(campo=campo,id=id))





admin.site.register(Categoria,AdminCategoria)
admin.site.register(Produttore,AdminProduttore)
admin.site.register(Stampante,AdminStampante)
admin.site.register(Prodotto,AdminProdotto)
admin.site.register(Serie,AdminSerie)
admin.site.register(Colore,AdminColore)

