# Performances en matière de sécurité IBM

## Verify - Gestion de l'identité et de l'accès

### Vérifier les exemples

#### Vérifier l'utilitaire d'assistance

Ce répertoire contient des exemples de code pour le téléchargement et l'énumération de fichiers à l'usage de Verify Support.

### Table des matières

* [Utilisation de l'exemple](#usage-of-the-example)
* [Scénarios et témoignages d'utilisateurs](#scenariosuser-stories)
* [Construction de l'exemple](#building-the-example)

### Utilisation de l'exemple
```text
Usage: verifySupportUtility [auth|status|upload|list|results|help] -tenantURL tenantURL [-uploadFile filename] [-uploadComment comment] [-resultsFile filename]
Usage of verifySupportUtility:
        command is one of [ auth, status, upload, list, results, help ]
        (default is 'help')
  -help
        Display the full help text
  -loglevel integer
        Logging Level (default 0)
        0=report success/failure, status codes, response times  (default)
        1=report include response body
        2=report include request body
        3=report full trace (for debugging)
  -tenantURL tenantURL
        URL used to contact tenant: client:secret@tenant.domain
  -uploadFile filename
        Optional file to upload to Verify
  -uploadComment comment
        Optional comment to include with upload to Verify
  -resultsFile filename
        Optional results file to download from Verify

auth	Authenticate to the tenant using the specified client and secret
status	Query status of the file upload service
upload	Upload the specified uploadFile to Verify
list	List uploaded files
results	List any results or download a results file
help	Display the full help text
```


### Scénarios et témoignages d'utilisateurs

* Le client souhaite fournir un fichier volumineux à SRE via un canal sécurisé.
* Le SRE demande au client d'utiliser l'utilitaire d'assistance Verify avec son locataire.
* Le client crée un client API, ou utilise un client existant, dans son locataire.

#### Vérifier que les informations d'identification du client de l'API fonctionnent

```text
$ verifySupportUtility auth -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com
Successfully authenticated to mytenant.verify.ibm.com
```

#### Vérifier que le service répond

```text
$ verifySupportUtility status -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com
Service is responding
Status is good
```

#### Envoyer un fichier par téléchargement

```text
$ verifySupportUtility upload -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com -uploadFile newUsers.csv -uploadComment "New users for load on Jan 17"
Successfully uploaded newUsers.csv
```

* Une fois le fichier téléchargé, le SRE le traite, par exemple en le chargeant en masse.

#### Liste des fichiers téléchargés

* Le client peut dresser la liste des fichiers qu'il a téléchargés, afin de s'assurer qu'ils ont bien été reçus.

```text
$ verifySupportUtility list -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com
Upload time                     Filename    	Actual	Requested	Comment
2022-01-16 09:41:18 -0600 CST	test.txt    	28  	28      	Test ldif for bulkload
2022-01-17 20:58:13 -0600 CST	newUsers.csv	6901677	6901677 	New users for load on Jan 17
```

#### Liste des fichiers de résultats

* Le client peut voir les résultats d'un fichier téléchargé, par exemple un chargement groupé

```text
$ verifySupportUtility results -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com
Results time                    Filename	    Status	        Comment                     	Id
2022-01-18 11:07:20 -0600 CST	newUserIds.csv	Load complete	New users for load on Jan 17     41f751bc7a26bce1879c1613109fdccd
```

#### Consulter un fichier de résultats

```text
$ verifySupportUtility results -tenantURL XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:YYYYYYYY@mytenant.verify.ibm.com -resultsFile 41f751bc7a26bce1879c1613109fdccd
```


### Construction de l'exemple

Le répertoire bin contient des binaires liés statiquement pour [Linux](bin/linux/verifySupportUtility), [Mac](bin/darwin/verifySupportUtility) et
 [Windows](bin/windows/verifySupportUtility.exe)

Ceux-ci ne nécessitent pas d'exécution et devraient simplement fonctionner sur le système d'exploitation correspondant.

Si go est installé, vous pouvez compiler les trois binaires sous Linux en utilisant le script make.sh  
Les développeurs Mac et Windows devraient être en mesure de créer un script similaire.   
Notez que vous aurez besoin de l'[installation go de golang.org](https://golang.org/doc/install) afin d'être sûr de créer des binaires statiques
statiques.  Le paquetage gccgo fourni par RedHat crée des binaires liés dynamiquement qui nécessitent l'installation d'un moteur d'exécution go avant de s'exécuter
avant de pouvoir s'exécuter.

<!-- v2.3.7 : caits-prod-app-gp_webui_20241231T140349-16_en_fr -->