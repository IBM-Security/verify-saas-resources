# Performances en matière de sécurité IBM

## Verify - Gestion de l'identité et de l'accès

### Vérifier les exemples

#### Hacheur CSV

Ce répertoire contient un exemple de code permettant de pré-hacher les mots de passe dans un fichier CSV avant de créer des utilisateurs à l'aide des API de vérification.
Cela vous permet de hacher les mots de passe au moment où ils sont extraits d'un registre d'utilisateurs existant,

### Table des matières

* [Utilisation de l'exemple](#usage-of-the-example)
* [Construction de l'exemple](#building-the-example)

### Utilisation de l'exemple
```text
Usage csvHasher -input_file csv_file -output_file csv_file [-column_name column_name | -column_number column_number] [-hash_size 256 | 512]
   csvHasher converts the specified column of a CSV file to SHA256 or SHA512 format usable as an ldap password
   The format generated is consistent with https://docs.ldap.com/specs/draft-stroeder-hashed-userpassword-values-01.txt

```

L'utilitaire csvHasher accepte trois paramètres obligatoires (le nom de la colonne ou le numéro de la colonne peuvent être spécifiés) et deux paramètres facultatifs :
- input_file - Un fichier CSV contenant les enregistrements des utilisateurs
- output_file - Le nom d'un fichier CSV à créer avec les enregistrements d'utilisateurs traités
- column_name - Le nom de la colonne qui doit être remplacée par la valeur SHA256 formatée ldap des données
- column_number - Le numéro (à partir de 1) de la colonne qui doit être remplacée par la valeur SHA256 formatée ldap des données
- hash_size - La taille (256 ou 512) des hachages à générer.  La
   valeur prise par défaut est 256.
- help - Affiche le texte d'aide complet

Le format généré est conforme à https://docs.ldap.com/specs/draft-stroeder-hashed-userpassword-values-01.txt et est accepté par les API de Verify Cloud Directory
accepté par les API de Verify Cloud Directory.  Les valeurs hachées peuvent être substituées aux mots de passe en texte clair lors de la création ou de la modification d'utilisateurs via l'API
modification d'utilisateurs via l'API.

### Construction de l'exemple

Le répertoire bin contient des binaires liés statiquement pour [Linux](bin/linux/csvHasher), [Mac](bin/darwin/csvHasher) et
 [Windows](bin/windows/csvHasher)

Ceux-ci ne nécessitent pas d'exécution et devraient simplement fonctionner sur le système d'exploitation correspondant.

Si go est installé, vous pouvez compiler les trois binaires sous Linux en utilisant le script make.sh  
Les développeurs Mac et Windows devraient être en mesure de créer un script similaire.   
Notez que vous aurez besoin de l'[installation go de golang.org](https://golang.org/doc/install) afin d'être sûr de créer des binaires statiques
statiques.  Le paquetage gccgo fourni par RedHat crée des binaires liés dynamiquement qui nécessitent l'installation d'un moteur d'exécution go pour être exécutés
avant de pouvoir s'exécuter.

<!-- v2.3.7 : caits-prod-app-gp_webui_20241231T140353-5_en_fr -->