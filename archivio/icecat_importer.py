
from cartuccia24 import settings
from time import strftime, localtime
import requests
import xml.etree.cElementTree
import xml.etree.ElementTree
import os
from archivio import models
from io import StringIO

categorie_prodotti = list()
categorie_prodotti.append("283")
categorie_prodotti.append("373")
categorie_prodotti.append("374")
categorie_prodotti.append("375")
categorie_prodotti.append("377")
categorie_prodotti.append("378")
categorie_prodotti.append("379")
categorie_prodotti.append("380")
categorie_prodotti.append("692")
categorie_prodotti.append("702")
categorie_prodotti.append("843")
categorie_prodotti.append("846")
categorie_prodotti.append("905")
categorie_prodotti.append("915")
categorie_prodotti.append("917")
categorie_prodotti.append("978")
categorie_prodotti.append("981")
categorie_prodotti.append("1010")
categorie_prodotti.append("1148")
categorie_prodotti.append("1305")
categorie_prodotti.append("1472")
categorie_prodotti.append("1778")
categorie_prodotti.append("1791")
categorie_prodotti.append("2595")
categorie_prodotti.append("2758")
categorie_prodotti.append("3061")
categorie_prodotti.append("4426")

categorie_stampanti = list()
categorie_stampanti.append("159")
categorie_stampanti.append("197")
categorie_stampanti.append("225")
categorie_stampanti.append("227")
categorie_stampanti.append("228")
categorie_stampanti.append("229")
categorie_stampanti.append("230")
categorie_stampanti.append("231")
categorie_stampanti.append("234")
categorie_stampanti.append("235")
categorie_stampanti.append("302")
categorie_stampanti.append("304")
categorie_stampanti.append("916")
categorie_stampanti.append("922")
categorie_stampanti.append("1547")
categorie_stampanti.append("1594")
categorie_stampanti.append("1727")
categorie_stampanti.append("1727")
categorie_stampanti.append("2655")
categorie_stampanti.append("4161")



def write_log(msg,clear = False):
    if clear:
        file = open(settings.BASE_DIR+"/log.txt","w")
    else :
        file = open(settings.BASE_DIR+"/log.txt","a")
    file.write("# [{data}] {msg}\n".format(data=strftime("%Y-%m-%d %H:%M:%S", localtime()),msg=msg))
    print("# [{data}] {msg}".format(data=strftime("%Y-%m-%d %H:%M:%S", localtime()),msg=msg))
    file.close()


def downloadFile():
    write_log("Download file da icecat ")
    richiesta = requests.get("https://data.icecat.biz/export/freeurls/on_market.export_urls_rich.xml",
                             auth=("ipsoware", "56TYGHBN"), stream=True)
    write_log("Download file da icecat COMPLETATO ")

    try:
        os.mkdir(settings.BASE_DIR+"/downloads/")
    except:
        pass

    with open(settings.BASE_DIR+"/downloads/icecatfile.xml", 'wb') as fd:
        write_log("Scrittura dati sul disco ")
        for chunk in richiesta.iter_content(1024):
            fd.write(chunk)
        fd.close()
        write_log("Scrittura dati sul disco COMPLETATA")

def getUltimoIndice():
    indice = 0
    try:
        with open(settings.BASE_DIR + "/downloads/last_index.txt", "rb") as fd:
            indice = int(fd.readline())
    except:
        pass
    return indice

def writeUltimoIndice(indice):
    try:
        with open(settings.BASE_DIR + "/downloads/last_index.txt", "wb") as fd:
            fd.write(str(indice))
            fd.close()
    except:
        pass




def readFile():
    write_log("Lettura file XML dal disco")
    xmlDoc = xml.etree.cElementTree.parse(settings.BASE_DIR+"/downloads/icecatfile.xml")
    root = xmlDoc.getroot()
    productUrls = root.findall("ProductUrls")[0]
    prodotti = productUrls.findall("ProductUrl")

    write_log("Lettura file XML dal disco completata")
    write_log("Inserimento dati prodotti e ricerca stampanti")

    i = getUltimoIndice()

    print("Lettura dal numero {i}".format(i=i))

    while i < len(prodotti):
        prodotto = prodotti[i]
        if prodotto.attrib.get("Category_ID") in categorie_prodotti:
            try:
                importaProdotto(prodotto.attrib.get("product_id"), prodotto.attrib.get("prod_id"))
            except:
                pass
        elif prodotto.attrib.get("Category_ID") in categorie_stampanti:
            try:
                importaStampante(prodotto.attrib.get("product_id"), prodotto.attrib.get("prod_id"))
            except:
                pass
        writeUltimoIndice(i)
        i = i + 1


    write_log("Inserimento dati nel database COMPLETATO")

def importaProdotto(view_id,mpn):
    obj = None

    try:
        obj = models.Prodotto.objects.get(mpn=mpn)
    except:
        pass

    update = True

    if obj is None:
        if obj.icecat_id != "":
            update = False
            print("Prodotto {mpn} scartato ".format(mpn=mpn))

    if update:
        richiesta = requests.get(
            "https://data.icecat.biz/export/freexml.int/IT/" + view_id + ".xml",
            auth=("ipsoware", "56TYGHBN"), stream=True)

        xmlDoc = xml.etree.cElementTree.fromstring(richiesta.text.encode("utf8"))
        informazioni_base = xmlDoc.findall("Product")[0]
        img = informazioni_base.attrib.get("HighPic")
        try:
            categoria = informazioni_base.findall("Category")[0]
        except:
            pass
        try:
            produttore = informazioni_base.findall("Supplier")[0]
        except:
            pass

        codice_ean = ""
        try:
            eans = informazioni_base.findall("EANCode")[0]
            if eans.attrib.get("EAN") is not None:
                codice_ean = eans.attrib.get("EAN")
        except:
            eans = None

        descrizione_lunga = ""
        descrizione_breve = ""

        try:
            descrizioni = informazioni_base.findall("ProductDescription")[0]
            if descrizioni.attrib.get("LongDesc") is not None:
                descrizione_lunga = descrizioni.attrib.get("LongDesc")

            if descrizioni.attrib.get("ShortDesc") is not None:
                descrizione_breve = descrizioni.attrib.get("ShortDesc")
        except:
            pass

        if informazioni_base.attrib.get("Title") is not None:

            try:
                obj_category = models.Categoria.objects.get(icecat_id=categoria.attrib.get("ID"))
            except:
                obj_category = models.Categoria.objects.get(pk=33)

            if produttore is not None:
                obj_manufacturers = models.Produttore.objects.all().filter(icecat_id=produttore.attrib.get("ID"))

                if len(obj_manufacturers) == 0:
                    obj_manufacturer = models.Marca()
                    obj_manufacturer.nome = produttore.attrib.get("Name")
                    obj_manufacturer.icecat_id = produttore.attrib.get("ID")
                else:
                    obj_manufacturer = obj_manufacturers[0]
            else:
                obj_manufacturer = models.Produttore.objects.get(pk=3278)



            if obj is None:
                write_log("Prodotto da creare {mpn}".format(mpn=mpn))
                #Crea prodotto
                obj = models.Prodotto()
                obj.nome = informazioni_base.attrib.get("Title")
                obj.categoria = obj_category
                obj.marca = obj_manufacturer
                obj.ean = codice_ean
                obj.mpn = mpn
                obj.colore = models.Colore.objects.get(pk=8)
            else:
                write_log("Prodotto esistente {mpn}".format(mpn=mpn))
                if obj.categoria_id == 33:
                    obj.categoria = obj_category


            obj.descrizione_lunga = descrizione_lunga
            obj.descrizione_breve = descrizione_breve
            obj.icecat_id = view_id
            obj.url_image = img
            obj.save()

def importaStampante(view_id,mpn):
    obj = None

    try:
        obj = models.Stampante.objects.get(mpn=mpn)
    except:
        pass

    update = True

    if obj is not None:
        if obj.icecat_id != "":
            update = False
            print("Stampante {mpn} scartata ".format(mpn=mpn))

    if update:
        richiesta = requests.get(
            "https://data.icecat.biz/export/freexml.int/IT/" + view_id + ".xml",
            auth=("ipsoware", "56TYGHBN"), stream=True)

        xmlDoc = xml.etree.cElementTree.fromstring(richiesta.text.encode("utf8"))
        informazioni_base = xmlDoc.findall("Product")[0]
        img = informazioni_base.attrib.get("HighPic")
        try :
            categoria = informazioni_base.findall("Category")[0]
        except:
            pass
        try:
            produttore = informazioni_base.findall("Supplier")[0]
        except:
            pass

        codice_ean = ""
        try:
            eans = informazioni_base.findall("EANCode")[0]
            if eans.attrib.get("EAN") is not None:
                codice_ean = eans.attrib.get("EAN")
        except:
            eans = None

        descrizione_lunga = ""
        descrizione_breve = ""

        try:
            descrizioni = informazioni_base.findall("SummaryDescription")[0]
            descrizione_breve_xml = descrizioni.findall("ShortSummaryDescription")[0]
            descrizione_lunga_xml = descrizioni.findall("LongSummaryDescription")[0]

            if descrizione_lunga_xml.text is not None:
                descrizione_lunga = descrizione_lunga_xml.text

            if descrizione_breve_xml.text is not None:
                descrizione_breve = descrizione_breve_xml.text
        except:
            pass

        if informazioni_base.attrib.get("Title") is not None:

            try:
                obj_category = models.Categoria.objects.get(icecat_id=categoria.attrib.get("ID"))
            except:
                obj_category = models.Categoria.objects.get(pk=33)

            if produttore is not None:
                obj_manufacturers = models.Produttore.objects.all().filter(icecat_id=produttore.attrib.get("ID"))

                if len(obj_manufacturers) == 0:
                    obj_manufacturer = models.Marca()
                    obj_manufacturer.nome = produttore.attrib.get("Name")
                    obj_manufacturer.icecat_id = produttore.attrib.get("ID")
                else:
                    obj_manufacturer = obj_manufacturers[0]
            else:
                 obj_manufacturer = models.Produttore.objects.get(pk=3278)


            if obj is None:
                write_log("Stampante da creare {mpn}".format(mpn=mpn))
                # Crea prodotto
                obj = models.Stampante()
                obj.nome = informazioni_base.attrib.get("Title")
                obj.categoria = obj_category
                obj.marca = obj_manufacturer
                obj.ean = codice_ean
                obj.mpn = mpn
                obj.colore = models.Colore.objects.get(pk=8)
                obj.serie = models.Serie.objects.get(pk=142)
                try:
                    prodotti_correlati = informazioni_base.findall("ProductRelated")

                    for pr in prodotti_correlati:
                        pr_xml = pr.find("Product")
                        pr_objs = models.Prodotto.objects.filter(mpn=pr_xml.attrib.get("Prod_id"))

                        if len(pr_objs) > 0:
                            obj.prodotti_associati.add(pr_objs[0])
                except:
                    pass

            else:
                write_log("Stampante esistente {mpn}".format(mpn=mpn))
                if obj.prodotti_associati.count() == 0:
                    try:
                        prodotti_correlati = informazioni_base.findall("ProductRelated")

                        for pr in prodotti_correlati:
                            pr_xml = pr.find("Product")
                            pr_objs = models.Prodotto.objects.filter(mpn=pr_xml.attrib.get("Prod_id"))

                            if len(pr_objs) > 0:
                                obj.prodotti_associati.add(pr_objs[0])
                    except:
                        pass

                if obj.categoria_id == 33:
                    obj.categoria = obj_category

            obj.descrizione_lunga = descrizione_lunga
            obj.descrizione_breve = descrizione_breve
            obj.icecat_id = view_id
            obj.url_image = img
            obj.save()


