#Importiamo una serie di moduli:
#json: contiene la funzione 'dumps' che permette di codificare un dizionario in formato json
#pycurl: un'interfaccia Python alla libreria libcurl. Verra' utilizzata principalmente per scaricare la pagina web inserendo 'username' e 'password' dove quest'ultima verra' criptata.
#StringIO: la classe permette di creare una stringa che si "comporta" come un file. Infatti le istanze di tale classe hanno il metodo 'write'.
#re: modulo che implementa le 'espressioni regolari' in stile linguaggio Perl. Questo modulo e' disponibile dalla versione 1.5 di Python e nelle versioni precedenti c'era un modulo per le espressioni regolari in stile Emacs

import json
import pycurl
from pycurl import Curl
from StringIO import StringIO
import re

#La classe Scraper e' il cuore del nostro programma. Contiene un costruttore ed una serie di metodi che consentono di accedere alle varie risorse:
#__init__: ciascun costruttore in Python ha questo identificatore. Quando una classe contiene il metodo __init__, tutte le volte che viene creata un'istanza della classe viene invocato il costruttore per inizializzare i campi dell'oggetto appena creato. Ogni istanza della nostra classe contiene 'username' e 'password' che verranno utilizzati dal metodo __fetch_page per scaricare la pagina;
#__fetch_page: esegue il download della pagina
#__search_tag_contents: preleva il contenuto di un elemento HTML (es: il contenuto tra il tag di apertura <p> ed il tag di chiusura </p>. Inizialmente il metodo e' stato utilizzato, poi si e' scoperto che non serve piu' ai nostri scopi ma lo lasciamo perche' puo' tornarci utile in futuro
#riepilogo_esami, dati_personali, residenza, domicilio, libretto, pagamenti, prenotazioni_effettuate: questi metodi sono autoesplicativi e verranno spiegati in dettaglio piu' avanti

class Scraper : 

    #Costruttore: ciascun costruttore in Python ha come primo parametro un riferimento all'oggetto che si sta costruendo e che abbiamo chiamato 'self'. Per i programmatori C++ questo e' l'equivalente del puntatore 'this'. La convenzione prevede che il parametro venga chiamato in questo modo, ma nessuno ci impedisce di chiamarlo in altro modo. Per evitare confusione e rendere piu' leggibile il programma abbiamo preferito seguire la convenzione dei programmatori Python. Quando viene istanziata la classe, il parametro 'self' verra' inizializzato automaticamente da Python. Noi ci dobbiamo preoccupare di fornire solo 'username' e 'password' come se il costruttore richiedesse effettivamente 2 parametri
    def __init__(self, username, password) :
        self.__username = username
	self.__password = password

    #Il metodo __fetch_page scarica la pagina utilizzando le credenziali di accesso. Questo metodo si appoggia sulla classe pycurl ed in particolare all'uso del costruttore 'Curl'. Prima di tutto vengono inizializzate le variabili che costituiscono le intestazioni del messaggio di richiesta HTTP.
    #Anche in questo caso abbiamo il parametro 'self' e dobbiamo far finta che il metodo richieda obbligatoriamente solo il parametro 'url'
    def __fetch_page(self, url) :
        
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

    #Il metodo __search_tag_contents preleva il contenuto di un tag HTML tenendo conto di quelle situazioni in cui un tag e' contenuto in un tag dello stesso nome. Per esempio, se vogliamo prelevare il contenuto di un tag 'div' e questo contiene un altro tag 'div' allora il metodo capira' qual'e' il tag di chiusura corretto. Questa funzione e' identica al metodo 'getElementById' del DOM. Il metodo, inizialmente utilizzato nelle altre funzioni, non verra' usato ma lo lasceremo nel caso ci dovesse servire in futuro.

    #####################################################################################################################
    #I seguenti metodi vengono richiamati dal server quando si richiede la URL corrispondente.
    #Es: nel caso di 'riepilogo_esami' questo verra' invocato quando eseguiamo una post sulla URL 'http://students.uniparthenope.it:[num_port]/UniparthenopeEsse3API/riepilogo_esami'.
    #Tutti i metodi seguenti restituiranno un dizionario del tipo:
    #    {'nome_metodo': info_relative_al_metodo}
    #Inizialmente il dizionario e' del tipo:
    #    {'nome_metodo': None}
    #####################################################################################################################

    def login(self) :
        #Metodo per effettuare il login
	#La struttura dati 'result' e' del tipo: 
	#    {
	#        'login': 'valore'
	#    }
	#
	#'valore' e' '0' se le credenziali non sono corrette.
	#'valore' e' '1' se l'accesso e' stato effettuato con successo

	#Preleviamo la pagina SOLO per verificare se ci siamo autenticati
        result = {'login': '0' }
        url = 'https://uniparthenope.esse3.cineca.it/auth/Home.do'
        page = self.__fetch_page(url)

	#Se non ci siamo autenticati, viene restituito 'result' cosi' com'e' con 'valore' = '1'
	if not page : 
	    return result
	result['login'] = '1'
	#Codifica 'result' in formato JSON
	return result
    
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
	
	#Regex per prelevare il contenuto del tag 'dt' e del tag 'description'
	p = re.compile('<dt>(.*?)</dt>.*?<description>(.*?)</description>')
	#riepilogo_esami_dict e' un dizionario che conterra' tutte le informazioni relative al riepilogo esami.
        riepilogo_esami_dict = {}
	#Nella pagina web c'e' piu' di un tag 'dt' e di un tag 'description'. L'iteratore serve per ciclare tra tutti questi elementi
        it = p.finditer(page)
	#Preleva 'CFU conseguiti', 'Media Aritmetica', ecc. e questi verranni scritti con gli unserscore ed in minuscolo
        #Es: 'match.group(1)' restituisce 'Media Aritmetica' ed 'match.group(2)' restituisce '28'
	for match in it :
            riepilogo_esami_dict[match.group(1).lower().replace(' ', '_')] = match.group(2)
	#La chiave 'riepilogo_esami' del dizionario 'result' conterra' proprio 'riepilogo_esami_dict'
	result['riepilogo_esami'] = riepilogo_esami_dict
	#'result' viene codificato in formato JSON con le chiavi in ordine alfabetico
        return result

    def dati_personali(self) : 
        
	#Scarichiamo la pagina contenente i dati personali dello studente. Se 'username' e 'password' non sono corrette allora verra' restituita la struttura dati 'result' cosi' com'e'
        result = {'dati_personali': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Anagrafica/Anagrafica.do'
	page = self.__fetch_page(url)
	if not page : 
	    return result

	#Preleva il contenuto dal tag 'div' con id="idsummaryFormNestedTemplateBox_1"
	p = re.compile('<div[^>]*id="idsummaryFormNestedTemplateBox_1"[^>]*>(.*?)</div>')
	page = p.search(page).group(1)

	#Preleva il contenuto del tag 'dl'
	p = re.compile('<dl[^>]*>(.*?)</dl>')
	page = p.search(page).group(1)

        #Regex per prelevare il contenuto del tag 'dt' ed del tag 'description'
	p = re.compile('<dt>(.*?)</dt>.*?<description>(.*?)</description>')
	#Nella pagina web c'e' piu' di un tag 'dt' e di un tag 'description'. L'iteratore serve per ciclare tra tutti questi elementi
	it = p.finditer(page)
	#Il dizionario 'dati_personali_dict' conterra' tutti i dati personali dello studente.
	dati_personali_dict = {}
	#Preleva 'nome', 'codice fiscale', ecc. e questi verranno scritti con gli unserscore ed in minuscolo
	#Es: il metodo 'match.group(1)' restituisce 'Nome' e 'match.group(2)' restituisce 'Pippo'
	for match in it : 
	    dati_personali_dict[match.group(1).replace(' ', '_').lower()] = match.group(2)

	#La chiave 'dati_personali' del dizionario 'result' conterra' proprio 'dati_personali_dict'
        result['dati_personali'] = dati_personali_dict
	#'result' viene convertito in formato JSON con le chiavi in ordine alfabetico
	return result

    def residenza(self) : 
        #Scarica la pagina con i dati sulla residenza dello studente. Se 'username' e 'password' non sono corrette, restituisce la struttura dati 'result' cosi' com'e'
	result = {'residenza': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Anagrafica/Anagrafica.do'
        page = self.__fetch_page(url)
	if not page : 
	    return result

	#Regex per prelevare il contenuto del tag 'div' con id="idsummaryFormNestedTemplateBox_2"
	p = re.compile('<div[^>]*id="idsummaryFormNestedTemplateBox_2"[^>]*>(.*?)</div>')
	#Il metodo 'group(1)' restituisce il contenuto del tag trovato
	page = p.search(page).group(1)
	#Regex per prelevare il contenuto del tag 'dl'
	p = re.compile('<dl[^>]*>(.*?)</dl>')
	#Il metodo 'group(1)' restituisce il contenuto del tag 'dl'
	page = p.search(page).group(1)
	#Regex per prelevare il contenuto del tag 'dt' e del tag 'description'
	p = re.compile('<dt>(.*?)</dt>.*?<description>(.*?)</description>')
	#Nella pagina web c'e' piu' di un tag 'dt' e di un tag 'description'. L'iteratore serve per ciclare tra tutti questi elementi
	it = p.finditer(page)
	#Il dizionario 'residenza_dict' conterra' i dati sulla residenza dello studente
	residenza_dict = {}
	#Preleva 'Comune/Citta'', 'Numero Civico', ecc.
	#Le chiavi del dizionario saranno scritte con gli underscore ed in minuscolo
	#Il metodo 'group(1)' restituisce, ad esempio, 'Numero Civico' e 'group(2)' restituisce, ad esempio, 41
	for match in it : 
	    residenza_dict[match.group(1).lower().replace(' ', '_')] = match.group(2)

        #La chiave 'residenza' del dizionario 'result' avra' come valore proprio il dizionario 'residenza_dict'
	result['residenza'] = residenza_dict
	#'result' viene codificato in formato JSON con le chiavi in ordine alfabetico
	return result

    def domicilio(self) : 
        #Scarica la pagina relativa al domicilio dello studente. Il codice e' identico al metodo precedente. Per i commenti vedere il metodo qui sopra
        result = {'domicilio': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Anagrafica/Anagrafica.do'
        page = self.__fetch_page(url)
	if not page : 
	    return result
	#Regex per prelevare il contenuto del tag 'div' con id="idsummaryFormNestedTemplateBox_3"
	p = re.compile('<div[^>]*id="idsummaryFormNestedTemplateBox_3"[^>]*>(.*?)</div>')
	page = p.search(page).group(1)
	p = re.compile('<dl[^>]*>(.*?)</dl>')
	page = p.search(page).group(1)
	p = re.compile('<dt>(.*?)</dt>.*?<description>(.*?)</description>')
	it = p.finditer(page)
	domicilio_dict = {}
	for match in it : 
	    domicilio_dict[match.group(1).lower().replace(' ', '_')] = match.group(2)

        result['domicilio'] = domicilio_dict
	return result

    def libretto(self) : 
        #Scarica la pagina del libretto dello studente
        result = {'libretto': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Libretto/LibrettoHome.do'
	page = self.__fetch_page(url)
	#Se la pagina non puo' essere scaricata (se 'username' e 'password' sono sbagliate) restituisce la struttura 'result' cosi' com'e'
	if not page : 
	    return result
	
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
	    libretto_list[i-1][th_list[2]] = td_list[6]

	    #Stato
	    libretto_list[i-1][th_list[3]] = alt_pattern.search(td_list[7]).group(1)

	    #Anno Accademico di Frequenza
	    libretto_list[i-1][th_list[4]] = td_list[8]

	    #Voto - Data Esame
	    libretto_list[i-1][th_list[5]] = td_list[9]

        #La chiave 'librettro' della struttura 'result' avra' come valore proprio 'libretto_list' 
	result['libretto'] = libretto_list
	#'result' viene codificato in formato JSON con le chiavi in ordine alfabetico
        return result

    def pagamenti(self) : 
        #Scarichiamo la pagina contenente i pagamenti
        result = {'pagamenti': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Tasse/ListaFatture.do'
        page = self.__fetch_page(url)
        
	#Se 'username' e 'password' non sono corretti, restituisce la struttura 'result' cosi' com'e'
	if not page : 
	    return result

	#Regex per prelevare il contenuto della tabella dei pagamenti
        SearchStr ='<table cellspacing="0" cellpadding="0" border="0" class="detail_table">(.*?)</table>'

        p = re.search(SearchStr.decode('utf-8'), page.decode('utf-8'), re.I | re.U)
        table = p.groups()
	
	#Regex per prelevare il contenuto delle righe della tabella
	pattern = '<tr>(.*?)</tr>'
	#Crea una 
	tr_list = re.findall(pattern,table)
	tr_list_len = len(tr_list)
	
	#Regex per prelevare le intestazioni
	p = re.compile('<th[^>]*>(.*?)</th>')
	#Iteratore per tra le varie intestazioni
	it = p.finditer(tr_list[0])
	#Lista che conterra' le intestazioni
	th_list = []
	#Ciascuna intestazione verra' scritta con gli unserscore ed in minuscolo
	for match in it : 
	    th_list.append(match.group(1).lower().replace(' ', '_'))

	#Lista dei pagamenti. Ciascun elemento della lista e' un dizionario
	pagamenti_list = []
	
	#Regex per prelevare il contenuto del tag 'td'
	td_pattern = re.compile('<td[^>]*>(.*?)</td>')
	#Regex per prelevare il contenuto del tag 'a'
	a_pattern = re.compile('<a[^>]*>(.*?)</a>')
	#Regex per prelevare il contenuto del tag 'alt'
	alt_pattern = re.compile('alt="(.*?)"')
	
	#Cicliamo tra le righe della tabella. L'indice di partenza e' 1 perche' l'indice 0 corrisponde alla riga delle intestazioni che sono state gia' prelevate
	for i in range(1, tr_list_len) : 
	    #Aggiungiamo un dizionario vuoto alla lista
	    pagamenti_list.append({})
	    
	    #Crea una lista dove ogni elemento e' il contenuto di un tag 'td'
	    td_list = td_pattern.findall(tr_list[i])
	    #Numero di elementi della lista appena creata
	    td_list_len = len(td_list)
	    
	    #Preleva la 'Fattura'
	    pagamenti_list[i-1][th_list[0]] = a_pattern.search(td_list[0]).group(1)
	    
	    #Preleva 'Codice Bollettino', 'Anno', ...(tranne Stato)
	    for j in range(1, td_list_len-1) : 
	        pagamenti_list[i-1][th_list[j]] = td_list[j]
	    
	    #Preleva 'Stato'
	    pagamenti_list[i-1][th_list[td_list_len-1]] = alt_pattern.search(td_list[td_list_len-1]).group(1)

        #La chiave 'pagamento' della struttura 'result' avra' come valore proprio 'pagamenti_list'
	result['pagamenti'] = pagamenti_list
	#Codifica 'result' in formato JSON con le chiavi in ordine alfabetico
        
	return result

    def prenotazioni_effettuate(self) : 
        #Scarica la pagina relativa alle agli esami prenotati
        result = {'prenotazioni_effettuate': None}
        url = 'https://uniparthenope.esse3.cineca.it/auth/studente/Appelli/BachecaPrenotazioni.do'
        page = self.__fetch_page(url)
	#Se 'username' e 'password' non sono corrette restituisce la struttura 'result' cosi' com'e'
	if not page : 
	    return result
	
	#Regex per estrarre le tabelle della pagina. Con questa regex non siamo in grado di estrarre tutte le tabelle, ma quelle che non vengono estratte non servono al nostro scopo
	p = re.compile('<table[^>]*>.*?</table>')
	#Lista di tutte le tabelle
	tables = p.findall(page)
	#Se il numero di tabelle e' inferiore o uguale a 5 significa che non sono stati prenotati esami e viene restituito 'result' cosi' com'e'. Quando viene prenotato un solo esame il numero di tabelle passa a 6, e cosi' via
	if(len(tables) <= 5) : 
	    return result
	
	#Tra le tabelle ottenute prende solo quelle relative agli esami prenotati
	tables_tmp = []
	tables_len = len(tables)
	for i in range(4, tables_len, 2) : 
	    tables_tmp.append(tables[i])
	del tables
	#'tables' contiene solo le tabelle degli esami prenotati, le altre tabelle sono state cancellate
	tables = tables_tmp
	#Numero di tabelle estratte
	tables_len = len(tables)
	
	#Lista che conterra' le prenotazioni
	prenotazioni_effettuate_list = []
	
	#Regex per estrarre il contenuto del tag 'tr'
	tr_pattern = re.compile('<tr[^>]*>(.*?)</tr>')
	#Regex per estrarre il contenuto del tag 'th'
	th_pattern = re.compile('<th[^>]*>(.*?)</th>')
	#Regex per estrarre il contenuto del tag 'td'
	td_pattern = re.compile('<td[^>]*>(.*?)</td>')

	#Cicliamo tra le varie tabelle
	for i in range(0, tables_len) :
	    #Aggiungiamo un dizionario vuoto alla lista delle prenotazioni
	    prenotazioni_effettuate_list.append({})

	    #Estraiamo tutte le righe della tabella dell'esame prenotato
	    #tr_list[0] contiene il nome dell'esame
	    #tr_list[1] contiene il numero di iscrizione dell'esame
	    #tr_list[2] contiene il tipo di prova dell'esame (scritto o orale)
	    #Da tr_list[3] fino alla fine ci sono le restanti informazioni (giorno, ora, aula, ecc.)
	    tr_list = tr_pattern.findall(tables[i])
	    
	    #Preleviamo il nome dell'esame
	    prenotazioni_effettuate_list[i]['nome'] = th_pattern.search(tr_list[0]).group(1)

	    #Preleviamo il numero di iscrizione dell'esame facendo attenzione che ci sono i due puntini.
	    #Es: 'Numero Iscrizione: 1 su 2', noi dobbiamo estrarre solo cio' che si trova alla destra dei due puntini
	    prenotazioni_effettuate_list[i]['numero_iscrizione'] = th_pattern.search(tr_list[1]).group(1).split(':')[1]

	    #Preleviamo il tipo di prova. Stesso discorso di prima per quanto riguarda i due puntini
	    prenotazioni_effettuate_list[i]['tipo_prova'] = th_pattern.search(tr_list[2]).group(1).split(':')[1]

	    #Lista dei nomi delle intestazioni delle restanti informazioni
	    #Es: Giorno, Ora, ecc.
	    resto_header_list = th_pattern.findall(tr_list[3])
	    #Lista dei valori delle intestazioni delle restanti informazioni
	    #Es: 20/11/2000, 15:00, ecc.
	    resto_value_list = td_pattern.findall(tr_list[5])

	    #'prenotazioni_effettuate_list' contiene i dizionari relativi agli esami prenotati.
	    #Le chiavi dei dizionario vengono scritti con gli underscore ed in minuscolo
	    for j in range(0, 6) : 
	        prenotazioni_effettuate_list[i][resto_header_list[j].lower().replace(' ', '_')] = resto_value_list[j]

        #La chiave 'prenotazioni_effettuate' della struttura 'result' ha come valore proprio 'prenotazioni_effettuate_list
	result['prenotazioni_effettuate'] = prenotazioni_effettuate_list
	#Codifica 'result' in formato JSON con le chiavi in ordine alfabetico
	return result

