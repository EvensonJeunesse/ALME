séparateur de champs : ;
affectation -> : 
nom_du_champ:valeur;nom_du_champ:valeur;nom_du_champ:valeur;nom_du_champ:valeur;

syntaxe : en s'en fiche des retours à la ligne et des doubles espaces

champs : 

method: // Type de requête (WAIT, GET, HERE)

WAIT : requête d'attente de la detection d'un appareil et envoie d'informations lorsque l'appareil est détecté

GET : Avoir des informations sur un appareil détecté précedemment par le serveur

HERE : demande si l'appareil est actuellement présent 

device: //l'adresse mac hashé de l'appareil concerné , * signifie tous, rien signifie aucun 

info: // liste des informations sur le divice (utilisation change en fonction du type de requête

time:start_date,end_date // definition d'une demande de notification en cas de demande de detection d'un appareil au cours d'une periode 

route:ip,port //champ spécifiant l'adresse ip où renvoyer une requête en cas de détection de l'appareil, si non spécifié le callback se fera sur la machine source de la requete sur le port source

pass: // passphrase pour authoriser la connexion au serveur

encoding: //encoding utilisé pour l'envoie de la requête 

error: //champ pour l'insciption d'erreur lors du traitement de la requ^ete 