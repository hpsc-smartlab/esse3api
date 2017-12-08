# esse3api ESSE3 Web Application Program Interface

### Installazione con virtualenv ###

- virtualenv venv
- . venv/bin/activate
- pip install --editable .

### Server sicuro di produzione

Sarà presto disponibile https://api.uniparthenope.it

Al momento queste api non sono ancora state rilasciate per l'uso di produzione.


### Sviluppo ###

Queste API fanno uso di http://flask-restplus.readthedocs.io/ per la documentazione.

Nel file bin/esse3api è specificata la porta tcp su cui è aperto il server

http://localhost:12001

E' la url di default.

### Esecuzione in sviluppo ###

./bin/esse3api

### FAQ ###

- A cosa servono queste API?

A sviluppare applicazioni per dispositivi mobili che consentono di accedere ai servizi web di ESSE3.

- Sono ufficiali CINECA?

No, sono il frutto di sperimentazione.

- Coprono tutte le funzionalià?

No, ma sono open source (licenza MIT), quindi è possibile aggiugere nuove funzionalità e condividerle con gli altri sviluppatori.

- Così come sono possono essere usaete in produzione?

No, devono essere installate su di un server che assicura l'uso di https

- Posso modificare i miei voti?

No, non sei nel film WarGames (1983, https://it.wikipedia.org/wiki/Wargames_-_Giochi_di_guerra).

Puoi fare solo quello che puoi fare collegandoti via web a https://uniparthenope.esse3.cineca.it e sono con le tue credenziali.

- Posso implementare nuove funzionalità integrando altre api?

E' esattamente quello che mi aspetto.

- Quali devono essere le mie conoscenze informatiche per sviluppare queste api?

Python e Technologie Web. Il corso TW e il corso APRA2 forniscono queste competenze.

- Quali devono essere le mie conoscenze informatiche per utilizzare queste api?

iOS/Swift e Tecnologie Web. I corsi Apple, il corso TMM e il corso TW forniscono queste competenze.

### Etica ###

Queste API sono state rilasciate in open source al fine di contribuire alla cultura della programmazione per componenti, l'uso consapevole dei servizi web e la diffusione della cultura della creazione digitale al fine di invogliare le nuove generazioni ad essere creativi. Ogni uso non etico di questo strumento è disdicevole dove non legalmente pubibile o civilmente contestabile. Vale sempre il vecchio consiglio dello zio: "Grande potere, grande resposabilità".

