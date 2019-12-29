# ALME (Active Localisation of Mobile Equipment) SERVER

## Configuration : 
- Distribution linux 
- Python 3.* ou supèrieur
- Une carte réseau wifi acceptant le mode monitor
- Une autre carte réseau 

#### <span id="anchor"></span>Fonctionnement global

Notre capteur ALME devra être capable d'écouter (sniffer) le trafic wifi au alentour via une interface réseau en mode monitor. Il possède également une autre interface réseau qui lui permettra d'être connecté à un réseau et d’ouvrir un port dédié au serveur ALME afin de traiter les requêtes. Il devra ensuite pouvoir différencier les appareils entre eux. C'est à dire faire la différence entre les point d’accès et les appareils mobiles. Le capteur sera ensuite en mesure de récupérer la puissance du signal de chaque appareil ainsi que le moment de la dernière manifestation de ce dernier. Enfin le capteur pourra traiter les requêtes ALME telles que la demande de présence d'un appareil, la demande de notification lors de l'arrivé d'un appareil ainsi que la demande d'information sur un appareil.

#### <span id="anchor-1"></span>**Implémentation du serveur **

Le serveur ALME a été implémenté en python3. Il fournit une interface client sur le port qui par défaut est 1111. Il est nécessaire de spécifier au serveur quelle interface est en mode monitor lors du démarrage via l’option ( -i , -I ou --interface ). Vous pouvez également lui spécifier un autre port d’écoute que le 1111 avec l’option ( -p , -P ou --port ) .

La commande pour lancer le serveur est donc :

sudo python3 server.py -i \[interface\_wifi\] -p \[port\_d\_ecoute\]

exemple : sudo python3 server.py -i wlan0 -p 1112

#### <span id="anchor-2"></span>

#### <span id="anchor-3"></span>Connexion du client 

Pour établir une connexion il suffit au client de se connecter au port sur lequel le serveur ALME écoute. Il pourra ensuite envoyer ses requêtes. Pour faire les tests nous avons utilisé l’outil netcat qui permet d'établir une connexion TCP avec un serveur. Ici étant sur un seul ordinateur nous utiliserons l’adresse ip de loopback “127.0.0.1” pour que les segments ne sortent pas de l’ordinateur.

#### <span id="anchor-4"></span>**Structure du serveur : **

Le serveur possède 5 threads qui se séparent l'exécution des tâches.

1.  Un thread qui gère les nouvelles connexions des clients et leur associe un thread de gestion
2.  Un thread de gestion qui a pour but de réceptionner les données afin de reconstituer la liste des requêtes. Il positionne les requêtes dans une liste d’attente commune à tous les clients. C’est aussi lui qui va renvoyer la réponse des requêtes au client.
3.  Un thread qui va gérer les requêtes dans la file d’attente et va générer les réponses dans une autre file d’attente (pour l’envoie)
4.  Un thread qui analyse les trames et essaye d’extraire les informations sur les appareils
5.  Un thread qui se charge de changer les canaux d’écoute de l’interface réseau en mode monitor (le scanner ne scanne que les canaux les plus utilisés c’est à dire de 1 à 14). Ce thread ne privilégient pas les canaux 10 et 11 même si c’est les plus utilisés.

Le serveur est composé de 2 fichiers essentiels :

flc.py

Le fichier se trouve dans le dossier Falcon. Il contient le code du scanner de probes request/response et des beacons. Nous ne sauvegardons pas les adresses macs dans une base de données pour que notre expérience reste dans la légalité. Car si avions voulu les sauvegarder, nous aurions dû les anonymiser par des procédés de chiffrement.

Il est possible de lancer le scanner séparément. Il vous affichera les appareils qu’il a pu identifier ainsi que les informations sur ces appareils.

On peut y voir des informations comme l’adresse physique (mac) de l’appareil (partiellement cachée ici ), la puissance du signal, les réseaux wifi connus de l’appareil ainsi que le ssid de l’appareil si c’est un hotspot. On voit également la fréquence associée au canal de communication de l’appareil.

server.py

Le fichier se trouve à la racine du dossier. Il représente le serveur et contient le code gérant les threads nécessaires à la réception des requêtes, à leur traitement ainsi qu’à l’envoie de la réponse.

L’implémentation du serveur tient au total sur environ 700 lignes de code. Nous le détaillerons pas ici car ce n’est pas l’objet de l’étude.

### <span id="anchor-5"></span>b. Format d'une requête ALME

Pour le format des requêtes nous nous sommes inspiré des requêtes HTTP. Les requêtes doivent être composées de codes ASCII. Nous souhaitons utiliser le format JSON pour la structure interne des requêtes, elle doit donc respecter les règles de construction d'un document JSON:

1.  Il ne doit exister qu'un seul élément racine contenant tous les autres.
2.  Tout fichier JSON doit être soit un objet (délimité par "{" et "}" ), soit un tableau (délimité par "\[" et "\]" ).
3.  Les séparateurs utilisés entre deux paires de valeur sont des virgules.
4.  Un objet JSON peut en contenir d'autres.
5.  Il ne peut y avoir d'éléments croisés.

L'ordre des champs n'a pas d'importance.

Chaque requête doit suivre cette structure :

{ …. paramètres de la requête …. } ;

les accolades ( { , } ) délimitent la requête et le point virgule ( ; ) marque la fin de la requête. Il est donc possible d’envoyer plusieurs requêtes en même temps :

{ ….requête1…. } ; { ….requête2…. } ; { ….requête3…. } ;

Vous pouvez fermer la session en envoyant une requête spéciale “ ***exit;*** ”

Exemple de l’envoie d’une requête depuis le client et du traitement par le serveur :

1 - Connexion du client au serveur

client :

serveur :

2 - Envoie de la requête par le client

client :

******

3 - Traitement de la requête par le serveur

******

4 - Réception de la réponse par le client

******

### <span id="anchor-6"></span>c. Types de requêtes

#### <span id="anchor-7"></span>WAIT

La requête WAIT est une requête qui demande au serveur d'attendre jusqu'à la détection d'un ou de plusieurs appareils à l'intérieur d'une plage horaire donnée.

On peut interpréter cette requête comme la phrase intelligible suivante : *"Préviens moi si tu détectes ce ou ces appareils entre telle heure et telle heure"*.

Si le serveur détecte le ou les appareils durant cette plage d'horaire, il envoie la réponse au client en spécifiant quels appareils ont été détectés.

Si plusieurs adresses macs sont spécifiées le serveur répondra positivement si il trouve au moins un des appareils de la liste. La requête sera alors considérée comme traitée.

exemple :

{“type”:”wait”, “devices”:\[“c8:71:e8:81:88:23”, “ce:22:3f:f7:87:c8”\]};

{"type":"wait", "devices":\["e4:70:b8:ce:3e:e3", "2d:fd:a3:9d:ec:c8", "74:df:bf:1b:ea:cc"\]};

#### <span id="anchor-8"></span>GET

La requête GET permet d'obtenir des informations sur un appareil détecté précédemment par le serveur. Un seul appareil peut être spécifié dans une requête GET. Mais il est possible de demander la liste des adresses mac de tous les appareils détectés par le serveur.

On peut interpréter cette requête comme la phrase intelligible suivante : *"Donne moi les informations sur tel appareil"*.

Le serveur renvoie en réponse un objet JSON contenant des informations sur l’appareil en question.

*exemple : *{“type”:”get”, “devices”:\[“c8:71:e8:81:88:23”\]};

#### <span id="anchor-9"></span>HERE

La requête HERE a pour but de savoir si un appareil est actuellement présent dans le rayon de détection du serveur.

On peut interpréter cette requête comme la phrase intelligible suivante : *"Est ce que tu détectes que ce ou ces appareils sont actifs"*.

Le serveur répond à la requête dès la réception de cette dernière. Si l'appareil n'est pas dans la liste des appareils actifs du serveur lors de la réception le serveur renvoie une réponse négative. Dans le cas contraire le serveur envoie une réponse positive.

Un appareil est dit “actif” si ses informations ont été mis à jour il y a moins de 15 min.

Si plusieurs adresses macs sont spécifiées le serveur répondra positivement si il trouve au moins un des appareils de la liste. La requête sera alors considérée comme traitée.

exemple :

{“type”:”here”, “devices”:\[“c8:71:e8:81:88:23”\]};

{"type":"here", "devices":\["e4:70:b8:ce:3e:e3", "2d:fd:a3:9d:ec:c8", "74:df:bf:1b:ea:cc"\]};

#### <span id="anchor-10"></span>NOPE

La réponse NOPE est une réponse négative en réponse à une des 3 requêtes précédentes (WAIT,GET ou HERE). Elle contient en général les informations à l'origine de la réponse négative. Ce peut être dû à une erreur ou bien à la négation pure et simple de la demande.

*exemple de requête : *{“type”:”nope”, “devices”:\[“c8:71:e8:81:88:23”,“ce:22:3f:f7:87:c8”\]};

#### <span id="anchor-11"></span>YEP

La réponse YEP est une réponse positive en réponse à une des 3 requêtes précédentes (WAIT,GET ou HERE). Elle contient en général les informations demandées incluses dans une section particulière de la requête de réponse.

exemple de réponses :

requête HERE ou WAIT :

* *{“type”:”yep”, repid=”test” “devices”:\[“c8:71:e8:81:88:23”, “ce:22:3f:f7:87:c8”\]} ;

requête GET :

{"type": "yep", "repid": "127.0.0.1-50076-121517261701523740", "reqid": "test", "devices": \["“c8:71:e8:81:88:23"\], "date-time": "2019-12-15 17:26:1576430777", "info": {"device": {"mac": "“c8:71:e8:81:88:23", "last-seen": "2019-12-15 17:25:1576430731", "channel": 2412, "signal": -46.666666666666664, "know-ssids": \[\]}}, "errors": \[\]}

ERROR

La réponse ERROR indique qu’une erreur s’est produite lors du traitement de la requête et que celle-ci n’a pas pu aboutir. Le code des erreurs en cascades sont indiqués.

*exemple de réponse: *{“type”:”error”, “devices”:\[“c8:71e8:81:88:23”\], “errors”:\[{"code": 15, "details":"Wrong mac address"}\]} ;

### <span id="anchor-12"></span>d. Les champs d'une requête ALME

#### <span id="anchor-13"></span>type:

Ce champ spécifie le type de requête que l'on souhaite faire. Il ne peut prendre qu'une seule des différentes valeurs citées ci-dessous : WAIT, GET, HERE, NOPE, YEP, ERROR. si aucun valeur n'est spécifiée , la requête ne sera pas prise en compte par le serveur.

-   exemples

<!-- -->

-   requête côté client

"type":"wait"

"type":"get"

"type":"here"

-   réponse côté serveur

"type":"nope"

"type":"yep"

"type":"error"

#### <span id="anchor-14"></span>reqid :

Ce champ représente l’identifiant de la requête du côté client. Cela permet au client de savoir à quelle requête correspond une réponse du serveur et ainsi éviter la confusion dans le cas où les réponses arriveraient dans le désordre.

-   exemples

"reqid":"ab156"

si aucun identifiant n’est spécifiée, le champ sera vide &gt; "reqid":""

#### <span id="anchor-15"></span>repid :

Ce champ représente l’identifiant de la requête une fois traité par le serveur. Peut servir en cas de maintenance ou de recherche dans les logs du serveur si dans le futur il y a le besoin.

#### <span id="anchor-16"></span>devices:

Ce champ représente l'adresse mac du ou des appareils concernés par la requête. Lorsque l'on attribue la valeur \* à ce champ, le serveur va considérer que vous voulez désigner tous les appareils. Si aucun champ n’est spécifié la requête générera une erreur.

-   exemples

"devices":"\[mac\]"

"devices":\["mac1","mac2","mac3"\]

"devices":"\[\*\]";

#### <span id="anchor-17"></span>info

Liste des informations que le client souhaite obtenir sur le ou les appareils lors de la réponse du serveur. Les informations sont retournées sous format JSON.

-   exemples

"info":"{---JSON Object ---}";

la structure de l’objet info change en fonction des requêtes. Voici les différentes informations que vous pouvez obtenir via info :

-   “last-seen” : le moment de la dernière détection d’un appareil
-   “simple-devices” : listes des appareils qui ne sont pas des points d’accès
-   “networks” : listes des appareils qui sont des points d’accès
-   “device” : un appareil ainsi que les informations le concernant
-   “net-quantity” : la quantité de points d’accès détectés
-   “dev-quantity” : la quantité d’appareils hors points d’accès détectés
-   “total-quantity” : la somme net-quantity + dev-quantity

#### <span id="anchor-18"></span>time-range

Défini l'interval de temps pour lequel la requête est valide. il est nécessaire de spécifier un datetime sous le format :

 **\[“&lt;date&gt; &lt;time1&gt;”,“&lt;date&gt; &lt;time2&gt;”\]**

La partie **&lt;date&gt;** doit contenir l'année le mois ainsi que le jour de la requête. La partie **&lt;time&gt; **contient l'heure, les minutes et les secondes. Attention Il est nécessaire de spécifier un time-range uniquement pour les requêtes WAIT. Le champ sera ignoré dans les autres cas.

#### <span id="anchor-19"></span>date-time

Définie le moment ou la requête/réponse à été créé. La datetime doit correspondre au format [*ISO 8601*](https://en.wikipedia.org/wiki/ISO_8601) , c’est à dire : "YYYY-MM-DD HH:mm:ss"

-   YYYY : L'année
-   MM : Le mois
-   DD : le jour du mois
-   H : L'heure
-   m : Les minutes
-   s : les secondes

#### <span id="anchor-20"></span>errors:

Ce champ contient un tableau d'objets JSON qui représente les erreurs survenues durant le traitement de la requête. Elle est principalement renseignée lors de la création de requête de type "ERROR". Une erreur possède toujours 2 attributs : un attribut "code" qui spécifie le code associé à l'erreur et un attribut "details" qui est une chaîne de caractères décrivant le code d'erreur de manière concise. Les erreurs sont numérotées de 0 à 20.

-   exemples

"errors":"\[\]";

"errors":"\[{"code": 15, "details":"Description de l'erreur"}, .... ,{"code": 12, "details":"Description de l'erreur"}\]";
