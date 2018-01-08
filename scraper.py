# -*- coding: utf-8 -*-
import json
import pycurl
#from flask import jsonify
from pycurl import Curl
from StringIO import StringIO
import re
#from bs4 import BeautifulSoup
#import urllib2
#import urllib

class Scraper:

    def __init__(self,username,password):
        self.__username = username
        self.__password = password

    def __fetch_page(self, url) :
        useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
        encoding = 'gzip, deflate, sdch'
        httpheader = ['Accept: text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, */*; q=0.8', 'Accept-Language: it-IT, it; q=0.8, en-US; q=0.6, en; q=0.4', 'Host: uniparthenope.esse3.cineca.it']
        cookiefile = 'cookiefile'

        page = StringIO()
        c = Curl()
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEFUNCTION, page.write)
        c.setopt(c.COOKIEJAR, cookiefile)
        c.setopt(c.URL, url)
        c.perform()
        c.close()
        page.close()

        page = StringIO()
        c = Curl()
        c.setopt(c.USERPWD, self.__username + ':' + self.__password)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.WRITEFUNCTION, page.write)
        c.setopt(c.COOKIEFILE, cookiefile)
        c.setopt(c.ENCODING, encoding)
        c.setopt(c.HTTPHEADER, httpheader)
        c.setopt(c.REFERER, url)
        c.setopt(c.USERAGENT, useragent)
        c.setopt(c.URL, url)
        c.perform()

        if(c.getinfo(pycurl.HTTP_CODE) != 200) :
            return None
        c.close()

        page_str = page.getvalue()
        page.close()
        p = re.compile('\\s+')
        page_str = p.sub(" ", page_str)

        return page_str

#Questa funziona bene
    def login(self) :
        result = {'login': '0' }
        url = 'https://uniparthenope.esse3.cineca.it/auth/Home.do'
        page = self.__fetch_page(url)

        #Se non ci siamo autenticati, viene restituito 'result' cosi' com'e' con 'valore' = '1'
        if not page :
            return result
        result['login'] = '1'
        #Codifica 'result' in formato JSON
        return json.dumps(result)


#Questa funziona bene
    def libretto(self):
        result = {'libretto': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Libretto/LibrettoHome.do'
        page = self.__fetch_page(url) #Ho controllato e la pagina viene presa con successo
        if not page :
            return json.dumps(result)
        #soup=BeautifulSoup(page) #Utilizziamo BeautifulSoap per analizzare la pagina ottenuta
        #tables=soup.find_all('td',class_="detail_table") #Preleviamo tutte le tabelle
        #Regex per prelevare tutte le tabelle della pagina
	table_pattern = re.compile('<table[^>]*>.*?</table>')
	#Lista contenente tutte le tabelle
	tables = table_pattern.findall(page)
	
	#La tabella di nostro interesse, quella relativa al libretto, e' contenuto in 'tables[3]' e la copiamo in table
	table = tables[3]
	
	#Regex per prelevare tutte le righe della tabella
	tr_pattern = re.compile('<tr[^>]*>.*?</tr>')
	#Lista contenente tutte le righe della tabella
	tr_list = tr_pattern.findall(table);
	
	#Regex per prelevare tutte le intestazioni della tabella
	th_pattern = re.compile('<th[^>]*>(.*?)</th>')
	#Iteratore per 'scorrere' fra le intestazioni
	it = th_pattern.finditer(tr_list[0])
	#Lista che conterra' le intestazioni
	th_list = []
	#Ciascuna intestazione avra' gli underscore e sara' in minuscolo
	for match in it :
	    th_list.append(match.group(1).lower().replace(' ', '_'))
	
	for i in range(0,len(th_list)):
	    if(th_list[i]=='voto_-_data_esame'):
	        th_list[i] = 'voto'
	    if(th_list[i]=='attivit&agrave;_didattiche'):
	        th_list[i]='attivita'
	#print(th_list)
	
	#Numero di elementi nella lista delle righe
	tr_list_len = len(tr_list)
	#Lista che conterra' tutti gli esami presenti nel libretto
	libretto_list = []

	#Regex per prelevare il contenuto del tag 'td'
	td_pattern = re.compile('<td[^>]*>(.*?)</td>')
	#Regex per prelevare il contenuto del tag 'a'
	a_pattern = re.compile('<a[^>]*>(.*?)</a>')
	#Regex per prelevare il contenuto del tag 'alt'
	alt_pattern = re.compile('alt="(.*?)"')

	#Cicliamo tra le varie righe della tabella per prelevare tutte le informazioni relative agli insegnamenti.
	#Partiamo dall'indice 1 perche' l'indice 0 corrisponde alla riga contenente le intestazioni e queste ultime le abbiamo gia' prelevate.
	for i in range(1, tr_list_len) :
	    #Aggiungiamo un dizionario alla lista (ogni dizionario conterra' le informazioni relative ad un insegnamento)
            libretto_list.append({})
	    #Creiamo una lista di tutte le informazioni presenti in una riga della tabella (la riga relativa ad un insegnamento)
	    td_list = td_pattern.findall(tr_list[i])

	    #Anno Di Corso
	    libretto_list[i-1][th_list[0]] = td_list[0]

	    #Attivita Didattiche
	    libretto_list[i-1][th_list[1]] = a_pattern.search(td_list[1]).group(1)

	    #Peso in crediti
	    #libretto_list[i-1][th_list[2]] = td_list[6]

	    #Stato
	    libretto_list[i-1][th_list[3]] = alt_pattern.search(td_list[7]).group(1)

	    #Anno Accademico di Frequenza
	    libretto_list[i-1][th_list[4]] = td_list[8]

	    #Voto - Data Esame
	#    td_list[9]= filter(None,td_list[9])
	    unicode_string = unicode(td_list[9],"UTF-8")
	    unicode_string = unicode_string.replace('&nbsp;-&nbsp;',' - ')
	    libretto_list[i-1][th_list[5]] = unicode_string
	#    print(unicode_string)





#        libretto_list['attivita'] = libretto_list.pop(attivit&agrave;_didattiche)
#        print(libretto_list[1])
#        temp = '\"stato\"'
#        for i in range(0,len(libretto_list)):
#            if(libretto_list[i]== ''):
#                print(libretto_list[i])
#                break;
#        print(libretto_list)
        #La chiave 'librettro' della struttura 'result' avra' come valore proprio 'libretto_list'
	result['libretto'] = libretto_list
	#'result' viene codificato in formato JSON con le chiavi in ordine alfabetico
        #return jsonify(json.dumps(result, sort_keys=True))
        return json.dumps(result, sort_keys=True)



#ok questa funziona bene
    def riepilogo_esami(self) :

	#Scarichiamo la pagina contenente il riepilogo degli esami. Se non e' possibile fare questo, 'result' verra' restituito cosi' com'e'.
        result = {'riepilogo_esami': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/Home.do'
	page = self.__fetch_page(url)
	if not page :
	    return result

	#Preleva il contenuto del tag 'div' che ha id="gu-boxRiepilogoEsami" facendo uso delle regex.
	#La funzione 'compile' del modulo 're' restituisce un oggetto che rappresenta la nostra regex compilata e pronta per essere utilizzata su una stringa. Poi viene utilizzato il metodo 'search' per trovare la stringa corrispondente all'interno di 'page' e di questa viene presa la sottostringa che si trova tra le parentesi tonde della regex per evitare di includere nel risultato anche il tag di apertura e di chiusura (<div id="gu-... > e </div>). Il risultato lo poniamo in 'page' perche' il resto della pagine non ci interessa
        p = re.compile('<div id="gu-boxRiepilogoEsami" class="breaks1 record">(.*?)</div>')
        page = p.search(page).group(1)
	
	#Regex per prelevare il contenuto del tag 'dl'
        p = re.compile('<dl[^>]+>(.*?)</dl>')
        page = p.search(page).group(1)
        #print(type(page))
        unicode_string = unicode(page,"UTF-8")
        unicode_string = unicode_string.replace('&nbsp;<br>','')
        #print(unicode_string)
	
	#Regex per prelevare il contenuto del tag 'dt' e del tag 'description'
	p = re.compile('<dt>(.*?)</dt>.*?<dd>(.*?)</dd>')
	#riepilogo_esami_dict e' un dizionario che conterra' tutte le informazioni relative al riepilogo esami.
        riepilogo_esami_dict = {}
	#Nella pagina web c'e' piu' di un tag 'dt' e di un tag 'description'. L'iteratore serve per ciclare tra tutti questi elementi
        it = p.finditer(unicode_string)
	#Preleva 'CFU conseguiti', 'Media Aritmetica', ecc. e questi verranni scritti con gli unserscore ed in minuscolo
        #Es: 'match.group(1)' restituisce 'Media Aritmetica' ed 'match.group(2)' restituisce '28'
	for match in it :
            riepilogo_esami_dict[match.group(1).lower().replace(' ', '_')] = match.group(2)
	#La chiave 'riepilogo_esami' del dizionario 'result' conterra' proprio 'riepilogo_esami_dict'
	result['riepilogo_esami'] = riepilogo_esami_dict
	print(result)
	#'result' viene codificato in formato JSON con le chiavi in ordine alfabetico
        return json.dumps(result, sort_keys=True)


#Scritta da me e va bene!
    def pannello_di_controllo(self):
        result = {'pannello_di_controllo':None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/Home.do'
        page = self.__fetch_page(url)
        if not page:
            return result

#Troviamo la tabella
        p = re.compile('<table id="gu-homepagestudente-tablePanelControl" class="table-1" summary="Tabella contenente la situazione aggiornata dello studente">(.*?)</table>')
        table = p.search(page).group(1)

#Troviamo il tbody
        p = re.compile('<tbody[^>]*>(.*?)</tbody>')
        tbody_list = p.findall(table)

#Troviamo i tr
        p = re.compile('<tr[^>]*>(.*?)</tr>')
        tr_list = p.findall(tbody_list[0])

#Vengono presi tutti i td
        p = re.compile('<td[^>]*>(.*?)</td>')
        td_list0 = p.findall(tr_list[0]) #Preleviamo la lista dei td della prima riga
        td_list1 = p.findall(tr_list[1]) #Preleviamo la lista dei td della seconda riga
        td_list2 = p.findall(tr_list[2]) #Preleviamo la lista dei td della terza riga
        td_list3 = p.findall(tr_list[3]) #Preleviamo la lista dei td della quarta riga

#Preleviamo i contenuti dei tag <img> dei vari td e rimpiazziamo i valori che non ci servono
        img0 = td_list0[1].replace('<img src=\"images/stato_esito_r.gif\">&nbsp;scadute&nbsp;-&nbsp;','').replace('<img src="images/stato_esito_a.gif">&nbsp;','') #Tasse
        img1 = td_list1[1].replace('<img src=\"images/stato_esito_r.gif\">&nbsp;','').replace('<img src="images/stato_esito_a.gif">&nbsp;','') #Piano carriera
        img2 = td_list2[1].replace('<img src=\"images/stato_esito_v.gif\">&nbsp;','').replace('&nbsp;appelli disponibili','').replace('<img src="images/stato_esito_r.gif">&nbsp;','').replace('<img src="images/stato_esito_a.gif">&nbsp;','') #Appelli Disponibili
        img3 = td_list3[1].replace('<img src=\"images/stato_esito_r.gif\">&nbsp;','').replace('&nbsp;prenotazioni','').replace('<img src="images/stato_esito_a.gif">&nbsp;','').replace('1&nbsp;','') #Iscrizioni Appelli


        lista_0 = [td_list0[0],td_list1[0],td_list2[0],td_list3[0]] #Inseriamo i primi valori dei td in una lista
        lista_1 = [img0,img1,img2,img3] #Inseriamo i valori dei tag <img> in un'altra lista
        diz = {} #creiamo un dizionario vuoto

#Associamo le chiavi con i valori
        for i in range(0,len(lista_0)):
            diz[lista_0[i]]= lista_1[i]

        result['pannello_di_controllo'] = diz
#        print(result)
        return json.dumps(result,sort_keys=True)


#Scritta da me e va bene!
    def piano(self):
        result = {'piano':None}

        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Piani/PianiHome.do'
        page = self.__fetch_page(url)
        if not page:
            return result

        p = re.compile('<table cellspacing=\"0\" cellpadding=\"0\" border=\"0\" class=\"detail_table\">(.*?)</table>')
        tables = p.findall(page) #Trovata tutte le tabelle

        pattern_cod = '<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"5%\">.*?</th>'
        pattern_descr = '<th valign=\"top\" class=\"detail_table\" colspan=\"4\" id=\"\" rowspan=\"\" style=\"\" width=\"35%\">.*?</th>'
        pattern_stato = '<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"10%\">.*?</th>'
        pattern_peso = '<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"7%\">.*?</th>'

        #p = re.compile(pattern_cod)
        #p1 = re.compile(pattern_descr)
        #p2 = re.compile(pattern_stato)
        #p3 = re.compile(pattern_peso)

        #cod = p.findall(tables[0])
        #descr = p1.findall(tables[0])
        #stato = p2.findall(tables[0])
        #peso = p3.findall(tables[0])

#Lista contenente le intestazioni "codice,descrizione,stato,peso"
        #lista_int = [cod[0].replace('<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"5%\">','').replace('</th>',''),descr[0].replace('<th valign=\"top\" class=\"detail_table\" colspan=\"4\" id=\"\" rowspan=\"\" style=\"\" width=\"35%\">','').replace('</th>',''),stato[0].replace('<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"10%\">','').replace('</th>',''),peso[0].replace('<th valign=\"top\" class=\"detail_table\" colspan=\"\" id=\"\" rowspan=\"\" style=\"\" width=\"7%\">','').replace('</th>','')]

#Cerchiamo i codici esami
        pattern_td_cod = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"\" class=\"detail_table\">.*?</td>'
        p = re.compile(pattern_td_cod)
        cod_esami_t1 = p.findall(tables[0]) #Lista dei codici esami della tabella 1
        cod_esami_t2 = p.findall(tables[1]) #Lista dei codici esami della tabella 2
        cod_esami_t3 = p.findall(tables[2]) #Lista dei codici esami della tabella 3



#Eliminiamo i pattern che non ci servono dai codici esami trovati
        for i in range(0,len(cod_esami_t1)):
            cod_esami_t1[i] = cod_esami_t1[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')

        for i in range(0,len(cod_esami_t2)):
            cod_esami_t2[i] = cod_esami_t2[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')

        for i in range(0,len(cod_esami_t3)):
            cod_esami_t3[i] = cod_esami_t3[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')

        for i in range(0,len(cod_esami_t1)):
            if(cod_esami_t1[i]=='01240002'):
                cod_esami_t1[i] = 'TMOB'
            if(cod_esami_t1[i]=='01200002'):
                cod_esami_t1[i]='SIC'
            if(cod_esami_t1[i]=='794'):
                cod_esami_t1[i]='PFIN'

        for i in range(0,len(cod_esami_t2)):
            if(cod_esami_t2[i]=='01240002'):
                cod_esami_t2[i] = 'TMOB'
            if(cod_esami_t2[i]=='01200002'):
                cod_esami_t2[i]='SIC'
            if(cod_esami_t2[i]=='794'):
                cod_esami_t2[i]='PFIN'

        for i in range(0,len(cod_esami_t3)):
            if(cod_esami_t3[i]=='01240002'):
                cod_esami_t3[i] = 'TMOB'
            if(cod_esami_t3[i]=='01200002'):
                cod_esami_t3[i]='SIC'
            if(cod_esami_t3[i]=='794'):
                cod_esami_t3[i]='PFIN'

#        print(cod_esami_t1)
#        print(cod_esami_t2)
#        print(cod_esami_t3)

#Prendiamo tutte le descrizioni degli esami
        pattern_td_desc = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda.*?\">.*?</td>'
        p = re.compile(pattern_td_desc)
        desc_esami_t1 = p.findall(tables[0])
        desc_esami_t2 = p.findall(tables[1])
        desc_esami_t3 = p.findall(tables[2])

#Eliminiamo dai pattern trovati le parti di stringa che non ci interessano
        for i in range(0,len(desc_esami_t1)):
            desc_esami_t1[i] = desc_esami_t1[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda2\">','').replace('</td>','')

        for i in range(0,len(desc_esami_t2)):
            desc_esami_t2[i] = desc_esami_t2[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda2\">','').replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda1\">','').replace('</td>','')

        for i in range(0,len(desc_esami_t3)):
            desc_esami_t3[i] = desc_esami_t3[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda2\">','').replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"border-right: 0px none trasparent; \" rowspan=\"\" class=\"detail_table_middle legenda1\">','').replace('</td>','')


#Prendiamo tutti gli stati degli esami
        pattern_td_stato = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table\">.*?</td>'
        p = re.compile(pattern_td_stato)
        stato_esami_t1 = p.findall(tables[0])
        stato_esami_t2 = p.findall(tables[1])
        stato_esami_t3 = p.findall(tables[2])

#Eliminiamo dai pattern trovati le parti di stringa che non ci interessano
        for i in range(0,len(stato_esami_t1)):
            stato_esami_t1[i] = stato_esami_t1[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')

        for i in range(0,len(stato_esami_t2)):
            stato_esami_t2[i] = stato_esami_t2[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')

        for i in range(0,len(stato_esami_t3)):
            stato_esami_t3[i] = stato_esami_t3[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')


#Prendiamo tutti i pesi degli esami
        pattern_td_peso = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table_middle\">.*?</td>'
        p = re.compile(pattern_td_peso)
        peso_esami_t1 = p.findall(tables[0])
        peso_esami_t2 = p.findall(tables[1])
        peso_esami_t3 = p.findall(tables[2])

#Eliminiamo dai pattern trovati le parti di stringa che non ci interessano
        for i in range(0,len(peso_esami_t1)):
            peso_esami_t1[i] = peso_esami_t1[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table_middle\">','').replace('</td>','')

        for i in range(0,len(peso_esami_t2)):
            peso_esami_t2[i] = peso_esami_t2[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table_middle\">','').replace('</td>','')

        for i in range(0,len(peso_esami_t3)):
            peso_esami_t3[i] = peso_esami_t3[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:center; \" rowspan=\"\" class=\"detail_table_middle\">','').replace('</td>','')

        diz_t1 = {}
        diz_t2 = {}
        diz_t3 = {}

        for i in range(0,len(cod_esami_t1)):
            diz_t1[cod_esami_t1[i]] = (desc_esami_t1[i],stato_esami_t1[i],peso_esami_t1[i])

        for i in range(0,len(cod_esami_t2)):
            diz_t2[cod_esami_t2[i]] = (desc_esami_t2[i],stato_esami_t2[i],peso_esami_t2[i])

        for i in range(0,len(cod_esami_t3)):
            diz_t3[cod_esami_t3[i]] = (desc_esami_t3[i],stato_esami_t3[i],peso_esami_t3[i])

        result['piano'] = (diz_t1,diz_t2,diz_t3)
        return json.dumps(result,sort_keys=True)



#Scritta da me e funziona.Forse va migliorata poichè sembra che il dizionario di ritorno non torni tutti i valori anche se
#prese singolarmente ogni lista ritorna tutti i valori dell'utente
    def pagamenti(self):
        result = {'pagamenti':None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Tasse/ListaFatture.do'
        page = self.__fetch_page(url)
        if not page:
            return result

#        print(json.dumps(page))

#Troviamo la tabella che ci interessa
        pattern_table = '<table cellspacing=\"0\" cellpadding=\"0\" border=\"0\" class=\"detail_table\">.*?</table>'
        p = re.compile(pattern_table)
        table = p.findall(page)

#Prendiamo la lista dei 'codici bollettino' di ogni pagamento
        pattern_td_codici_bollettino = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"\" rowspan=\"1\" class=\"detail_table\">(\d{16,}|\d{,10})</td>'
        p = re.compile(pattern_td_codici_bollettino)
        lista_codici = p.findall(table[0])
        lista_codici = filter(None,lista_codici) #Eliminiamo gli spazi vuoti


#Prendiamo la lista degli anni.In lista2 saranno formattati gli anni in modo corretto.
        pattern_td_anno = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"\" rowspan=\"1\" class=\"detail_table\">(\d{2})\/(\d{2,2})</td>'
        p = re.compile(pattern_td_anno)
        lista_td_anno = p.findall(table[0])
        lista2 = []
        for i in range(0,len(lista_td_anno)):
            lista2.append(lista_td_anno[i][0])
            lista2[i] = lista2[i]+'/'+lista_td_anno[i][1]


#Prendiamo tutta la lista delle descrizioni
        pattern_td_descrizione ='<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"\" rowspan=\"\" class=\"detail_table\">\w+.*?</td>'
        p = re.compile(pattern_td_descrizione)
        lista_desc = p.findall(table[0])
        for i in range(0,len(lista_desc)):
            lista_desc[i] = lista_desc[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"\" rowspan=\"\" class=\"detail_table\">','').replace('</td>','')


#Prendiamo tutta la lista delle scadenze.In lista3 saranno formattate le scadenze in modo corretto
#            pattern_td_scadenza = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"\" rowspan=\"1\" class=\"detail_table\">(\d{2})\/(\d{2,2})\/(\d{4})</td>'
#            p = re.compile(pattern_td_scadenza)
#            lista_td_scad = p.findall(table[0])
#            lista3 = []
#            for i in range(len(lista_td_scad)):
#                lista3.append(lista_td_scad[i][0])
#                lista3[i] = lista3[i]+'/'+lista_td_scad[i][1]+'/'+lista_td_scad[i][2]


#Prendiamo tutti gli importi
            pattern_td_importo = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:right; \" rowspan=\"1\" class=\"detail_table\">.*?</td>'
            p = re.compile(pattern_td_importo)
            lista_td_imp = p.findall(table[0])
            for i in range(0,len(lista_td_imp)):
                lista_td_imp[i] = lista_td_imp[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:right; \" rowspan=\"1\" class=\"detail_table\">&euro;','').replace('</td>','')
                lista_td_imp[i] = lista_td_imp[i]+' euro'


#Prendiamo tutti gli stati dei pagamenti
            pattern_td_stato = '<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"1\" class=\"detail_table\">.*?</td>'
            p = re.compile(pattern_td_stato)
            lista_td_stati = p.findall(table[0])
            for i in range(0,len(lista_td_stati)):
                lista_td_stati[i] = lista_td_stati[i].replace('<td id=\"\" width=\"\" valign=\"\" colspan=\"\" style=\"text-align:left; \" rowspan=\"1\" class=\"detail_table\">','').replace('</td>','').replace('<img hspace=\"5 px\" src=\"images/semaf_v.gif\" title=\"','').replace('\">','').replace('<img hspace=\"5 px\" src=\"images/semaf_r.gif\" title=\"','')



        diz = {}
        for i in range(0,len(lista_desc)):
            diz[i] = (lista_desc[i],lista_td_imp[i],lista_td_stati[i])

        result['pagamenti'] = diz
        return json.dumps(result,sort_keys=True)
