# Performances en matière de sécurité IBM

## Verify - Gestion de l'identité et de l'accès

### Exemple de vérification - Gestion des utilisateurs

Ce répertoire contient du code d'exemple Golang pour la gestion en masse des utilisateurs à l'aide des API de Verify.  Le programme userManagement effectue
des actions sur un ensemble d'utilisateurs, notamment l'établissement d'une liste de jetons, la révocation de jetons et la désactivation des utilisateurs en définissant le mot de passe par un hachage impossible à comparer
à un hachage impossible à comparer.

### Table des matières

* [Documentation des API](#documentation-of-the-apis)
   * [Créer un client API](#create-an-api-client)
   * [Obtention d'un jeton d'accès](#get-an-access-token)
   * [Recherche d'utilisateurs](#lookup-users)
   * [Recherche de subventions](#lookup-grant)
   * [Supprimer la subvention](#delete-grant)
   * [Changer le mot de passe](#modify-password)
   * [Génération de la liste des utilisateurs](#list-users)
* [Utilisation de l'exemple](#usage-of-the-example)
* [Construction de l'exemple](#building-the-example)
* [Description des fichiers d'exemple](#descriptions-of-the-example-files)

### Documentation des API

Le [hub de documentation d' IBM Security Verify](https://docs.verify.ibm.com/verify/) fournit
des guides et de la documentation complets pour vous aider à commencer à travailler avec IBM Security Verify le plus rapidement possible,
ainsi qu'une assistance en cas de problème.

Les guides ["Getting Started"](https://docs.verify.ibm.com/verify/docs/guides) et surtout la documentation de l'API sont particulièrement intéressants pour ces exemples
et surtout la [documentation de l'API](https://docs.verify.ibm.com/verify/page/api-documentation), puisque le code de l'exemple
appelle une série d'API.

#### Créer un client API

La page de mise en route pour la [création d'un client API](https://docs.verify.ibm.com/verify/docs/create-api-client) décrit
comment créer un client d'API avec les accès appropriés.  L'ensemble des accès dont vous avez besoin pour appeler chaque API est décrit dans la documentation de cette API
la documentation de l'API en question.
* Pour [Obtenir des utilisateurs](https://docs.verify.ibm.com/verify/reference/getusers), le droit requis est readUserGroups (Lire les utilisateurs et les groupes) ou manageUserGroups (Gérer les utilisateurs et les groupes) ou manageAllUserGroups (Synchroniser les utilisateurs et les groupes) ou manageUserStandardGroups (Gérer les utilisateurs et les groupes standard).
   Note : Vous n'avez besoin que d'un seul droit, mais vous pouvez en avoir plusieurs.
* Pour les [subventions en lecture](https://docs.verify.ibm.com/verify/reference/readgrants_0), l'habilitation requise est readOidcGrants (Lire les subventions OIDC et OAuth) ou manageOidcGrants (Gérer les subventions OIDC et OAuth)
* Pour [supprimer une subvention](https://docs.verify.ibm.com/verify/reference/deletegrant), l'habilitation requise est manageOidcGrants (gérer les subventions OIDC et OAuth)
* Pour [Patch User](https://docs.verify.ibm.com/verify/reference/patchuser), le droit requis est manageUserGroups (Gérer les utilisateurs et les groupes) ou manageAllUserGroups (Synchroniser les utilisateurs et les groupes) ou manageUserStandardGroups (Gérer les utilisateurs et les groupes standard) ou updateAnyUser (Mettre à jour n'importe quel utilisateur).

Un ensemble minimal qui serait juste suffisant pour appeler les quatre API serait readUserGroups, manageOidcGrants et updateAnyUser.

#### Obtention d'un jeton d'accès

La première chose que tout programme devra faire avant d'appeler les API est d'obtenir un jeton d'accès, qu'il transmettra ensuite à chaque API qu'il appellera
chaque API qu'il appelle.  La page de mise en route pour les [informations d'identification du client](https://docs.verify.ibm.com/verify/docs/get-an-access-token)
décrit l'obtention du jeton d'accès pour effectuer des appels API, à l'aide de l'ID client et du secret générés lors de la création du client API
lorsque vous avez créé le client API. Les jetons d'accès ont une durée de vie limitée. Il est donc important pour un programme de longue durée de s'assurer qu'il n'utilise pas un jeton d'accès expiré
n'utilise pas un jeton d'accès expiré.

La page [Obtenir le jeton d'accès](https://docs.verify.ibm.com/verify/reference/handletoken) de la documentation de l'API est la référence de l'API pour cet appel
Référence API pour cet appel.  Chaque page décrit ce que fait l'API, ce que sont les paramètres d'entrée et les champs de données du formulaire, ainsi que les types et les valeurs autorisées
ainsi que les types et les valeurs autorisées.  Sur le côté droit de la page se trouvent des exemples de code en 16 langues
ainsi que des exemples de lignes de commande curl, avec des exemples de réponses positives et négatives.

En lisant les fonctions clés du code d'exemple, vous pouvez les comparer au code d'exemple Go dans la documentation de l'API.
Le jeton d'accès est récupéré dans [doAuth.go](doAuth.go) dans la fonction doAuth( ).  Son expiration est vérifiée et actualisée dans la fonction
la fonction checkAuth( ).

#### Recherche d'utilisateurs

La page [Obtenir des utilisateurs](https://docs.verify.ibm.com/verify/reference/getusers) de la documentation de l'API décrit comment rechercher des utilisateurs spécifiques
des utilisateurs spécifiques.  L'exemple userManagement l'utilise pour rechercher les informations fournies, telles que le nom d'utilisateur ou l'adresse électronique, afin d'obtenir l'identifiant de chaque utilisateur à transmettre lors d'appels ultérieurs
afin d'obtenir l'identifiant de chaque utilisateur à transmettre lors des appels suivants.

Le code de recherche de l'utilisateur se trouve dans [lookupUser.go](lookupUser.go), dans la fonction lookupUser( ).

#### Recherche de subventions

La page [Lire les subventions de la](https://docs.verify.ibm.com/verify/reference/readgrants_0) documentation de l'API décrit comment
récupérer une liste des subventions associées à un utilisateur spécifique. L'exemple userManagement l'utilise pour rechercher les subventions associées à l'identifiant de l'utilisateur qui a été renvoyé par )
associées à l'identifiant renvoyé par lookupUser( ).

Le code de recherche des subventions se trouve dans [listTokens.go](listTokens.go), dans la fonction listTokens( ).

#### Supprimer la subvention

La page [Supprimer une subvention de la](https://docs.verify.ibm.com/verify/reference/deletegrant) documentation de l'API décrit comment
supprimer une subvention spécifique. L'exemple userManagement l'utilise pour supprimer chaque subvention renvoyée par listTokens( ).

Le code de suppression des subventions se trouve dans le [fichier revokeTokens.go](revokeTokens.go), dans la fonction revokeTokens( ).

#### Changer le mot de passe

La page [Utilisateur du patch](https://docs.verify.ibm.com/verify/reference/patchuser) de la documentation de l'API décrit comment
modifier les attributs d'un utilisateur spécifique. L'exemple userManagement l'utilise pour modifier le mot de passe de l'utilisateur qui a été
retourné par lookupUser( ). La définition d'un hash invalide pour le mot de passe garantit que l'utilisateur devra passer par le processus de réinitialisation du mot de passe avant que cet identifiant puisse s'authentifier
avant de pouvoir s'authentifier. La modification du mot de passe de l'utilisateur entraîne également la révocation des jetons existants.

Le code de modification de l'utilisateur se trouve dans le fichier [disableUser.go](disableUser.go), dans la fonction disableUser( ).

#### Génération de la liste des utilisateurs

La page [Obtenir des utilisateurs](https://docs.verify.ibm.com/verify/reference/getusers) de la documentation de l'API décrit comment rechercher un ensemble d'utilisateurs
d'un ensemble d'utilisateurs.  L'exemple userManagement l'utilise pour rechercher tous les utilisateurs du locataire, par ordre d'identification, et pour rechercher les utilisateurs qui n'ont pas d'attribut lastLogin, ce qui signifie qu'ils ne se sont pas connectés depuis la création du compte
sans l'attribut lastLogin, ce qui signifie que l'utilisateur ne s'est pas connecté depuis la création du compte.

Le code de la liste des utilisateurs se trouve dans [listUsers.go](listUsers.go), dans la fonction listUsers( ).

### Utilisation de l'exemple
```text
Usage: userManagement [auth|listTokens|listUsers|revokeTokens|disableUser|help] -tenantURL tenantURL -userFile filename -userAttribute attributename
Usage of userManagement:
        command is one of [ auth, listTokens, listUsers, revokeTokens, disableUser, help ]
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
  -userFile filename
        Optional file containing a list of users
  -userAttribute attributename
        The attribute referred to by the list of users (default userid)

auth		Authenticate to the tenant using the specified client and secret
listTokens	List tokens for each user in the userFile
listUsers	Lookup all users in the tenant and list any that have never logged in
revokeTokens	Revoke tokens for each user in the userFile
disableUser	Disable each user in the userFile
help		Display the full help text

```

Le programme userManagement accepte 6 commandes :
- auth - S'authentifier auprès du locataire en utilisant le client et le secret spécifiés
- listTokens- Liste des jetons pour chaque utilisateur dans le userFile
- listUsers- Recherche tous les utilisateurs du locataire et liste ceux qui ne se sont jamais connectés
- revokeTokens- Révoque les jetons pour chaque utilisateur dans le userFile
- disableUser- Désactive chaque utilisateur dans le userFile
- help - Affiche le texte d'aide complet

Le userFile doit contenir une liste d'utilisateurs, un par ligne, identifiés par leur nom d'utilisateur, leur adresse électronique ou tout autre attribut consultable,
sur lesquels l'action sera effectuée. Le paramètre userAttribute indique à userManagement l'attribut à utiliser lors de la recherche.

Le programme userManagement parcourt la liste des utilisateurs, recherche chaque utilisateur et applique l'action spécifiée.
La désactivation de l'utilisateur s'effectue en attribuant à son mot de passe une valeur de hachage invalide qui ne peut pas être comparée.

La définition du niveau de journalisation peut être utile pour mieux comprendre les appels à l'API et pour le débogage.

### Construction de l'exemple

Le répertoire bin contient des binaires liés statiquement pour [Linux](bin/linux/userManagement), [Mac](bin/darwin/userManagement) et
 [Windows](bin/windows/userManagement)

Ceux-ci ne nécessitent pas d'exécution et devraient simplement fonctionner sur le système d'exploitation correspondant.

Si go est installé, vous pouvez compiler les trois binaires sous Linux en utilisant le script make.sh  
Les développeurs Mac et Windows devraient être en mesure de créer un script similaire.   
Notez que vous aurez besoin de l'[installation go de golang.org](https://golang.org/doc/install) afin d'être sûr de créer des binaires statiques
statiques.  Le paquetage gccgo fourni par RedHat crée des binaires liés dynamiquement qui nécessitent l'installation d'un moteur d'exécution go pour être exécutés
avant de s'exécuter.

### Description des fichiers d'exemple

#### [main.go](main.go)

Elle contient la fonction main()qui appelle d'abord getArguments( ) pour analyser les arguments de la ligne de commande et effectuer un certain
de la ligne de commande et effectuer quelques vérifications. Il appelle ensuite getUsers( ) pour lire le userFile et établir une liste de toutes les valeurs trouvées, une par ligne.  Il appelle ensuite
doAuth( ) pour s'authentifier avec l'identifiant du client, le secret et le locataire transmis dans l'argument de ligne de commande tenantURL.  Si la commande était
l'une des actions listTokens, revokeTokens, ou disableUser, et qu'un userAttribute a été spécifié, la fonction lookupUser( est appelée pour chaque
est appelée pour chaque utilisateur du userFile afin de trouver l'identifiant de l'utilisateur correspondant. Ensuite, listTokens( ), revokeTokens( ) ou disableUser( ) est appelée pour chaque
est appelée pour chacun des utilisateurs renvoyés par lookupUser.

#### [doAuth.go](doAuth.go)

Elle contient la fonction doAuth( ), qui appelle l'API token pour obtenir un jeton d'accès.  Il est enregistré par main() dans la structure configInfo
et toutes les autres fonctions le transmettent en tant que jeton Bearer dans un en-tête Authorization lors de leurs appels à l'API.
Cela se présente comme suit
```text
req.Header.Add("Authorization", "Bearer "+configInfo.accessToken)
```
Ce fichier contient également la fonction checkAuth( ) qui appelle doAuth( ) si le jeton a expiré.  Toutes les autres fonctions appellent
checkAuth( ) avant d'appeler leur API.

#### [lookupUser.go](lookupUser.go)

Il contient la fonction lookupUser( ), qui appelle l'API Users pour trouver un utilisateur correspondant à chaque ligne du userFile.  Le paramètre
userAttribute détermine l'attribut qui est transmis à l'appel Users avec une recherche d'égalité. Il est prévu que
chaque ligne du userFile corresponde à un seul utilisateur du locataire, de sorte que seul le premier résultat est examiné.  Si un résultat est renvoyé
est renvoyé, l'identifiant de l'utilisateur est renvoyé à l'appelant.

#### [listTokens.go](listTokens.go)

Elle contient la fonction listTokens( ), qui appelle l'API des subventions pour trouver tous les jetons correspondant à l'identifiant renvoyé par lookupUser
retourné par lookupUser.

#### [revokeTokens.go](revokeTokens.go)

Elle contient la fonction revokeTokens( ), qui appelle l'API des subventions pour supprimer chaque jeton renvoyé par listTokens( ).

#### [disableUser.go](disableUser.go)

Il contient la fonction disableUser( ), qui appelle l'API Utilisateurs pour modifier le mot de passe de l'utilisateur en un hash invalide.  Cela se fait
avec l'opération PATCH qui prend une structure json décrivant l'attribut exact à modifier, l'opération (ajouter/supprimer/remplacer)
et la valeur.

#### [listUsers.go](listUsers.go)

Elle contient la fonction listUsers( ), qui appelle l'API Utilisateurs pour obtenir une liste des utilisateurs du locataire, puis signale les utilisateurs qui ne se sont pas connectés
qui ne se sont pas connectés.  Pour ce faire, il appelle de manière répétée getUserList( ) avec le prochain userId pour commencer, et la liste des attributs
à renvoyer.  L'API Utilisateurs renvoie jusqu'à 2500 utilisateurs par appel.  Pour chaque ensemble d'utilisateurs renvoyés, la filterUserList( )
est appelée pour rechercher les utilisateurs sans l'attribut lastLogin et imprimer l'identifiant, l'adresse électronique et l'heure de création de l'utilisateur.  Cette fonction
cette fonction peut être modifiée pour effectuer tout autre traitement souhaité des informations relatives à l'utilisateur.

<!-- v2.3.7 : caits-prod-app-gp_webui_20241231T140338-15_en_fr -->