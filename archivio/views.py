from django.shortcuts import render
from django.http.response import HttpResponse
from archivio import icecat_importer
from archivio.models import *

# Create your views here.
def runProcess(request):
    #icecat_importer.downloadFile()
    icecat_importer.readFile()
    return HttpResponse("Processo completato")

def generateSlug(request):

    for modello in Stampante.objects.all().filter(slug__exact=""):
        modello.slug = slugify(str(modello.id)+" "+modello.nome)
        modello.save()

    for prodotto in Prodotto.objects.all().filter(slug__exact=""):
        prodotto.slug = slugify(str(prodotto.id) +" "+ prodotto.nome)
        prodotto.save()

    return HttpResponse("Processo completato")