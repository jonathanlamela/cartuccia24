from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
# Create your models here.

class Servizio(models.Model):
    codice_servizio = models.CharField(max_length=255,blank=False,unique=True)
    nome = models.CharField(max_length=255,blank=False)
    codice_versione = models.IntegerField(blank=False,default=1000)

    def __str__(self):
        return self.nome.encode('utf8')

    def __unicode__(self):
        return self.nome.encode('ascii')

    class Meta:
        verbose_name_plural = "Servizi"

class ClienteAPI(models.Model):
    nome = models.CharField(max_length=255,blank=False)
    cognome = models.CharField(max_length=255,blank=False)
    c_fiscale = models.CharField(max_length=255,blank=True,verbose_name="Codice fiscale")
    p_iva = models.CharField(max_length=255,blank=True,verbose_name="P. IVA")
    azienda = models.CharField(max_length=255,blank=True)
    via = models.CharField(max_length=255,blank=True)
    citta = models.CharField(max_length=255,blank=True,verbose_name="Citta")
    cap = models.CharField(max_length=255,blank=True)
    n_telefono = models.CharField(max_length=255,blank=True)
    n_cellulare = models.CharField(max_length=255,blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return "{cognome} {nome} ".format(cognome=self.cognome.encode("utf8"),nome=self.nome.encode("utf8"))

    def __unicode__(self):
        return "{cognome} {nome} ".format(cognome=self.cognome.encode("utf8"),nome=self.nome.encode("utf8"))

    class Meta:
        verbose_name_plural = "Clienti API"

class Licenza(models.Model):
    cliente = models.ForeignKey(ClienteAPI)
    servizio = models.ForeignKey(Servizio)
    codice_licenza = models.TextField(blank=False)
    data_inizio = models.DateField(blank=False,default=timezone.now)
    data_fine = models.DateField(blank=False,default=timezone.now)

    def __str__(self):
        return self.codice_licenza.encode("utf8")

    class Meta:
        verbose_name_plural = "Licenze"
