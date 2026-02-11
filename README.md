# TD-03 : Ransomeware

## 1. Contexte du Projet

Dans le cadre du TD de cybersécurité, l'objectif de ce projet est de développer un **ransomware pédagogique** pour comprendre les mécanismes de chiffrement utilisés dans les logiciels malveillants. Le projet se concentre sur quatre axes principaux : la **génération sécurisée de clés de chiffrement**, le **stockage local des clés** dans un répertoire sécurisé (`/varkeys`), **l'envoi sécurisé des clés vers un serveur distant** via SFTP, et le **chiffrement de fichiers et dossiers sélectionnés** par l'utilisateur. Ce projet permet ainsi d'aborder de manière pratique les bonnes pratiques de sécurité liées à la gestion des clés et au chiffrement des données dans un environnement contrôlé.


---

## 2. Spécifications Fonctionnelles

### Partie A : Vérification des Dépendances

Avant toute utilisation du script de chiffrement, il est essentiel de s'assurer que l'environnement Python dispose de toutes les bibliothèques nécessaires. Cette étape permet de prévenir les erreurs d'exécution liées à des modules manquants et garantit que les fonctionnalités de chiffrement et de transfert SFTP fonctionneront correctement.

Le script inclut une fonction `verification_dependance()` qui effectue les vérifications suivantes :

1. **Version de Python** : le script nécessite **Python 3.8 ou supérieur** pour assurer la compatibilité avec les bibliothèques utilisées.  
2. **Modules Python requis** : les modules `cryptography`, `paramiko` et `tqdm` sont nécessaires pour le chiffrement, la gestion des clés et l'affichage des barres de progression lors du traitement de plusieurs fichiers.  
3. **Installation automatique des dépendances** : si un module est manquant, le script propose de l'installer automatiquement à partir du fichier `requirements.txt` à l'aide de `pip`.  

Cette vérification préalable permet de garantir un fonctionnement stable du système et d'assurer que toutes les fonctionnalités de chiffrement, déchiffrement et transfert des clés sont disponibles avant toute opération sur les fichiers.

### Partie B : Menu Principal

Le script principal est structuré autour d'un **menu interactif** permettant à l'utilisateur de naviguer facilement entre les différentes fonctionnalités du projet. Le menu centralise toutes les actions nécessaires pour gérer les clés et effectuer le chiffrement ou le déchiffrement des fichiers.

Le menu propose les options suivantes :  

1. **Générer une clé**  
   L'utilisateur peut choisir de créer une clé AES aléatoire ou une clé dérivée d'un mot de passe via PBKDF2. La clé est ensuite sauvegardée localement dans un fichier JSON avec des permissions sécurisées (`600`) pour limiter l'accès aux seuls utilisateurs autorisés.  

2. **Envoyer une clé via SFTP**  
   Cette option permet de transférer de manière sécurisée une clé vers un serveur distant en utilisant le protocole SFTP. L'utilisateur renseigne les informations de connexion (hôte, nom d'utilisateur, mot de passe et chemin distant).  

3. **Chiffrer des fichiers ou dossiers**  
   L'utilisateur peut sélectionner un fichier unique ou un dossier complet pour le chiffrement. Chaque fichier est chiffré avec AES-CBC et un IV aléatoire, garantissant que même des fichiers identiques auront un chiffrement unique. Le padding PKCS7 est appliqué pour gérer les fichiers dont la taille n'est pas multiple de 16 octets.  

4. **Déchiffrement des fichiers**  
   Cette option permet de restaurer les fichiers à leur état initial en utilisant la clé correspondante. L'IV est extrait des 16 premiers octets du fichier, et le padding PKCS7 est retiré après le déchiffrement.  

5. **Vérifier les dépendances**  
   Permet de relancer la vérification des modules Python nécessaires et de s'assurer que le script peut fonctionner correctement.  

6. **Quitter le programme**  
   Termine l'exécution du script de manière sécurisée.  

Le menu principal constitue ainsi l'interface utilisateur du projet, simplifiant l'accès à toutes les fonctionnalités et structurant le déroulement des opérations de chiffrement, déchiffrement et gestion des clés.

### Partie C : Génération de Clés

La génération sécurisée des clés est une étape cruciale pour garantir la confidentialité des fichiers chiffrés. Dans ce projet, deux méthodes de génération de clés sont proposées :  

1. **Clé aléatoire AES**  
   - Une clé est générée aléatoirement en utilisant le module `secrets` de Python.  
   - La longueur de la clé peut être choisie par l’utilisateur parmi 128, 192 ou 256 bits, conformément aux standards AES.  
   - Cette méthode est rapide et sécurisée, car chaque clé est unique et imprévisible.  

2. **Clé dérivée d’un mot de passe (PBKDF2)**  
   - L’utilisateur saisit un mot de passe maître, qui est utilisé pour générer une clé via l’algorithme **PBKDF2**.  
   - Un **salt aléatoire** est ajouté pour chaque dérivation afin de renforcer la sécurité contre les attaques par dictionnaire ou par force brute.  
   - Le nombre d’itérations (390 000) permet d’augmenter le temps nécessaire à un attaquant pour tester des mots de passe.  

#### Stockage des clés

- Les clés générées sont sauvegardées dans un répertoire sécurisé (`./keys`) sous forme de fichiers JSON encodés en Base64.  
- Les permissions des fichiers sont restreintes (`600`) afin que seule la personne qui a généré la clé puisse y accéder.  
- Cette étape garantit que les clés sont à la fois **disponibles pour le chiffrement/déchiffrement** et **protégées contre tout accès non autorisé**.  

Cette approche permet de combiner **sécurité**, **flexibilité** et **traçabilité** des clés dans un environnement pédagogique de laboratoire.

### Partie D : Transfert SFTP

Le transfert sécurisé des clés est une étape importante pour simuler la communication d’un ransomware ou pour sécuriser la gestion des clés dans un environnement de laboratoire. Dans ce projet, le protocole **SFTP (SSH File Transfer Protocol)** est utilisé pour garantir la confidentialité et l’intégrité des clés lors de leur envoi vers un serveur distant.  

#### Fonctionnalités du transfert SFTP

1. **Connexion sécurisée**  
   - L’utilisateur renseigne l’adresse du serveur, le nom d’utilisateur, le mot de passe et le chemin distant de destination.  
   - La connexion est établie via SSH, assurant le chiffrement de toutes les données échangées.  

2. **Envoi de la clé**  
   - La clé locale, sauvegardée au format JSON et encodée en Base64, est transférée vers le serveur distant.  
   - Le protocole SFTP empêche l’interception ou la modification des fichiers pendant le transfert.  

3. **Gestion des erreurs**  
   - Le script prévoit la gestion des erreurs de connexion, d’authentification et de transfert, avec affichage des messages explicites pour guider l’utilisateur.  

#### Objectif pédagogique

Cette fonctionnalité permet de comprendre :  
- L’importance de **transférer des informations sensibles de manière sécurisée**.  
- L’utilisation d’un protocole fiable comme SFTP pour protéger les clés de chiffrement.  
- La mise en pratique de bonnes pratiques en cybersécurité dans un environnement de laboratoire contrôlé.  

Ainsi, le transfert SFTP complète le processus de chiffrement en simulant la **gestion sécurisée et distante des clés**, comme cela pourrait être observé dans des attaques réelles ou dans des architectures sécurisées de gestion de secrets.

### Partie E : Sélection et Chiffrement

Cette partie du projet concerne la sélection des fichiers ou dossiers à chiffrer ainsi que le processus de chiffrement proprement dit. Elle illustre le fonctionnement pratique du système et permet de mettre en œuvre les concepts de cryptographie appris en TD.  

#### Sélection des fichiers

- L’utilisateur peut choisir entre **un fichier unique** ou **un dossier complet**.  
- Dans le cas d’un dossier, le script parcourt récursivement tous les fichiers présents et les ajoute à la liste à traiter.  
- Cette flexibilité permet de tester le chiffrement sur différents types de fichiers et de comprendre l’impact du chiffrement sur des structures de dossiers entières.  

#### Processus de chiffrement

1. **Lecture du fichier**  
   - Les fichiers sont ouverts en mode binaire pour garantir que tous types de fichiers (texte, images, binaires) peuvent être traités.  

2. **Génération d’un IV aléatoire**  
   - Pour chaque fichier, un vecteur d’initialisation (IV) de 16 octets est généré aléatoirement.  
   - Cela garantit que deux fichiers identiques auront des fichiers chiffrés différents.  

3. **Padding PKCS7**  
   - Les fichiers dont la taille n’est pas un multiple de 16 octets sont complétés avec un padding PKCS7 pour s’adapter aux exigences du chiffrement AES-CBC.  

4. **Chiffrement AES-CBC**  
   - La clé générée précédemment est utilisée avec l’IV pour chiffrer les données du fichier.  
   - Le résultat final contient l’IV suivi des données chiffrées, ce qui permet de récupérer l’IV lors du déchiffrement.  

5. **Écriture du fichier chiffré**  
   - Le fichier d’origine est remplacé par sa version chiffrée.  
   - Le processus est appliqué à tous les fichiers sélectionnés, avec affichage d’une barre de progression via `tqdm` pour suivre l’avancement.  

### Partie F : Fonctionnalités Avancées

Cette partie met en avant les **fonctionnalités supplémentaires** du projet qui améliorent l’expérience utilisateur et la robustesse du système de chiffrement.  

#### 1. Chiffrement récursif des sous-dossiers

- Lorsqu’un dossier est sélectionné pour le chiffrement, le script parcourt **tous les sous-dossiers** et chiffre tous les fichiers qu’ils contiennent.  
- Cette approche garantit que l’intégralité du contenu d’un dossier, y compris les sous-structures, est protégée.  
- L’utilisateur n’a pas besoin de sélectionner chaque fichier manuellement, ce qui rend le processus plus efficace et pratique.

#### 2. Barre de progression pour les opérations longues

- Pour les dossiers contenant de nombreux fichiers, le script utilise la bibliothèque `tqdm` pour afficher une **barre de progression**.  
- Cela permet à l’utilisateur de visualiser l’avancement du chiffrement ou du déchiffrement, et de mieux gérer son temps lors d’opérations longues.  
- La barre de progression améliore l’ergonomie et rend l’interface plus interactive.

---

## Utilisaton

1. Lancer le script :

    ```bash
    python main.py
2. Suivre le menu interactif :

    ```bash
    ==============================
    Système de Chiffrement - TP3
    ==============================
    1. Générer une clé
    2. Envoyer une clé via SFTP
    3. Chiffrer fichiers (LAB ONLY)
    4. Déchiffrement du fichier
    5. Vérifier dépendances
    6. Quitter

    Choix : 
---

## Schéma de fonctionnement

    
    [Utilisateur] 
     │
     ▼
    Génération clé (AES / PBKDF2)
        │
        ▼
    Clé sauvegardée (JSON / Base64)
        │
        ▼
    Sélection fichier(s) à chiffrer
        │
        ▼
    Chiffrement AES-CBC
        │
        ├─ IV aléatoire (16 octets)
        └─ Padding PKCS7
        ▼
    Fichier chiffré → Stocké sur disque
        │
        ▼
    Déchiffrement
        │
        └─ Récupération IV
        └─ Suppression padding
        ▼
    Fichier restauré en clair

---

## Bonnes pratiques et sécurité

- Permissions des clés : fichiers JSON protégés (600) pour éviter toute fuite.

- IV aléatoire : garantit que chaque fichier chiffré est unique même si le contenu est identique.

- Padding PKCS7 : assure que le chiffrement AES fonctionne pour tous types de fichiers.

- PBKDF2 : protège les clés dérivées de mots de passe grâce à un salt et un grand nombre d’itérations.

- SFTP : transfert des clés via SSH pour éviter leur interception.

- Ne jamais réutiliser l’IV pour le même fichier ou clé.
