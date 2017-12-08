import json
import pycurl
from pycurl import Curl
from StringIO import StringIO
import re

def __init__(self, username, password) :
        self.__username = username
	self.__password = password

def fetch_page(url) :
        
	#Intestazioni del messaggio di richiesta HTTP
        #useragent: questo e' il corrispondente dell'intestazione 'User-Agent' del protocollo HTTP. E' un'indicazione del tipo di Browser che si sta utilizzando per navigare in rete. Naturalmente non faremo uso di alcun Browser e tutto cio' che faremo e' solamente scaricare una pagina, senza interpretarne il codice HTML. Questa intestazione consente di 'ingannare' il server facendogli credere che stiamo utilizzando un Browser ordinario per eseguire le normali funzioni previste dalla piattaforma Esse3;
        #encoding: questo e' l'equivalente dell'intestazione 'Accept-Encoding'. Indica una serie di codifiche che siamo propensi ad accettare da parte del server che contatteremo;
        #httpheader: una lista (simile ad un array) di stringhe dove ciascuna stringa e' del tipo 'attributo: valore'. Contiene tutte le restanti intestazioni del protocollo HTTP oltre a quelle che abbiamo appena descritto:
            #Accept: per indicare la tipologia di dati che possiamo ricevere senza problemi;
            #application: il tipo di applicazione accettata;
            #image: il formato immagine accettato;
            #Accept-Language: in quale lingua accettiamo la pagina richiesta;
            #Host: semplicemente l'hostname del server che contatteremo.
        #cookiefile: il nome di un file di cookie che verra' creato localmente quando eseguiremo la prima richiesta HTTP. Quando i siti web richiedono 'username' e 'password' di solito chiedono al client di creare un cookie di sessione per evitare che l'utente inserisca molte volte le sue credenziali di accesso.
        
	useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
        encoding = 'gzip, deflate, sdch'
        httpheader = ['Accept: text/html, application/xhtml+xml, application/xml; q=0.9, image/webp, */*; q=0.8', 'Accept-Language: it-IT, it; q=0.8, en-US; q=0.6, en; q=0.4', 'Host: uniparthenope.esse3.cineca.it']
        cookiefile = 'cookiefile'

	#La prima richiesta HTTP serve per creare il cookie di sessione che verra' salvato locamente
	#La variabile 'page' e' di tipo 'StringIO', una classe che implementa una stringa che 'imita' un file e le sue operazioni di Input/Output. 'page' sara' il contenuto della pagina scaricata.
	#Creiamo un'istanza della classe class 'Curl' ed settiamo una serie di opzioni che influenzeranno la richiesta:
	#FOLLOWLOCATION: se la pagina scaricata contiene l'intestazione 'Location: ' Curl effettuera' una nuova richiesta HTTP scegliendo come URL quella specificata proprio da 'Location';
	#WRITEFUNCTION: serve per specificare una funzione che verra' invocata quando dovra' essere salvata la pagina. La funzione da invocare e' la funzione 'write' dell'oggetto StringIO
	#COOKIEJAR: gli diamo il nome del file di cookie che dovra' essere creato qualora il server lo richiedesse;
	#URL: semplicemente l'URL della pagina che vogliamo scaricare.

	#Infine viene eseguito il metodo 'perform' per eseguire la richiesta.
	page = StringIO()
        c = Curl()
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.WRITEFUNCTION, page.write)
        c.setopt(c.COOKIEJAR, cookiefile)
        c.setopt(c.URL, url)
        c.perform()
        c.close()
	page.close()
        
        #Una volta ottenuto il cookie creiamo un nuovo oggetto 'Curl' per eseguire la seconda richiesta. Questa volta verranno utilizzate, oltre alle intestazioni HTTP precedentemente specificate, 'username' e 'password' assieme al file di cookie.
	#L'opzione 'REFERER' serve solo per indicare al server la pagina che abbiamo contattato immediatamente prima.
	page = StringIO()
        c = Curl()
        c.setopt(c.USERPWD, '0124000039' + ':' + 'susanna89')
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.WRITEFUNCTION, page.write)
        c.setopt(c.COOKIEFILE, cookiefile)
        c.setopt(c.ENCODING, encoding)
        c.setopt(c.HTTPHEADER, httpheader)
        c.setopt(c.REFERER, url)
        c.setopt(c.USERAGENT, useragent)
        c.setopt(c.URL, url)
        c.perform()

	#Il metodo 'getinfo' ci da' informazioni su cosa e' accaduto dopo aver eseguito la richiesta. Un'informazione che ci interessa in particolare e' il codice di stato. Se il codice e' diverso da 200 molto probabilmente non abbiamo inserito 'username' e 'password' corretti e verra' ritornato un valore 'None' che e' l'equivalente di 'NULL' in C++. Se il codice di stato e' 200 significa che tutto e' andato bene.
	if(c.getinfo(pycurl.HTTP_CODE) != 200) : 
	    return None
	c.close()

	#Il metodo 'getvalue' e' per restituire un tipo 'str' (cioe' Stringa) a partire da un oggetto di tipi 'StringIO'.
	#La funzione 'compile' fa parte del modulo 're' delle espressioni regolari. Faremo largo uso delle regex (d'ora in avanti le espressioni regolari verranno chiamate cosi') come in questo caso che vengono eliminati tutti i caratteri non stampabili (\n, \t, ecc.) dalla pagina per facilitare l'uso delle successiva regex applicate sempre alla stessa pagina.
	page_str = page.getvalue()
	page.close()
	p = re.compile('\\s+')
	page_str = p.sub(" ", page_str)

	#Restituisce la pagina web sottoforma di stringa
	return page_str

#Scarichiamo la pagina contenente i pagamenti
url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Tasse/ListaFatture.do'
page = fetch_page(url)
SearchStr ='<table cellspacing="0" cellpadding="0" border="0" class="detail_table">(.*?)</table>'

Result = re.search(SearchStr.decode('utf-8'), page.decode('utf-8'), re.I | re.U)
print Result.groups()
	