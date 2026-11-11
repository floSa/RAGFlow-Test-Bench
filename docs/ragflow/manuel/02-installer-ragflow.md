# 02. Installer RAGFlow

> Ce chapitre apprend à installer RAGFlow sous Windows 11 avec WSL2, à créer le premier compte, puis à démarrer, arrêter et désinstaller l'application.
> **Point de départ** : un terminal Ubuntu ouvert sous Windows (menu Démarrer › « Ubuntu »), machine préparée comme décrit dans « Ce qu'il faut savoir ».
> **Durée** : environ 15 minutes, dont une à deux minutes de téléchargement. **Avant** : chapitre 01.

**Attention** : l'installation officielle de RAGFlow ouvre sa base de données et ses fichiers à tout le réseau local avec des mots de passe connus de tous ; la méthode décrite ici les garde sur le poste (adresse `127.0.0.1`) et génère des mots de passe aléatoires. Ne pas lancer le fichier officiel tel quel sur un portable connecté à un réseau partagé.

## Ce qu'il faut savoir

RAGFlow ne s'installe pas comme un programme Windows : il tourne dans **Docker**, un outil qui fait fonctionner des applications prêtes à l'emploi, appelées conteneurs, à l'intérieur d'Ubuntu (WSL2). RAGFlow en utilise six : l'application elle-même, un moteur de recherche, une base de données, un stockage de fichiers, une mémoire tampon et une file d'attente des tâches. Les modèles d'IA tournent à part, dans un service commun appelé **LLM-Service**, partagé avec d'autres applications. Une fois installé, RAGFlow s'ouvre dans le navigateur de Windows, à l'adresse `http://127.0.0.1:8088`, comme un site web, mais visible de ce poste seulement.

Ce qu'il faut avant de commencer :

- Windows 11 avec WSL2 et une distribution Ubuntu ;
- Docker en marche dans Ubuntu (Docker Desktop avec l'intégration WSL2 activée, ou Docker installé dans Ubuntu) ;
- LLM-Service installé (dépôt séparé), avec un modèle de réponse et le modèle `bge-m3` ;
- 16 Go de mémoire au moins (32 Go avec une carte graphique), 10 Go de disque libre ;
- les autres applications gourmandes arrêtées, pour libérer la mémoire.

## Préparer l'installation

**Étape 1. Récupérer les fichiers d'installation**
*Où* : terminal Ubuntu, dans le dossier de travail choisi.
Copier le dépôt qui contient les scripts d'installation, puis s'y placer :

```bash
git clone https://github.com/floSa/RAGFlow-Test-Bench.git
cd RAGFlow-Test-Bench
```

*Résultat* : le dossier `RAGFlow-Test-Bench` existe ; toutes les commandes suivantes se lancent depuis ce dossier.

**Étape 2. Vérifier la machine**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer le diagnostic. Il ne modifie rien : il relève la mémoire, le disque, la version de Docker, la présence d'une carte graphique et un réglage de mémoire du système (`vm.max_map_count`) dont le moteur de recherche de RAGFlow a besoin.

```bash
outils/communs/diagnostic.sh
```

*Résultat* : un résumé de la machine s'affiche. Le réglage `vm.max_map_count` doit valoir au moins 262 144 ; s'il est plus bas, le moteur de recherche ne démarrera pas (voir « En cas de problème »).

**Étape 3. Démarrer le service de modèles**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer LLM-Service. Avec une carte graphique NVIDIA, la version vLLM (celle des essais de ce manuel) :

```bash
outils/communs/llm_service_vllm.sh
```

Sans carte graphique, la version Ollama :

```bash
outils/communs/llm_service.sh
```

*Résultat* : le script confirme que le service répond et liste les modèles présents. S'ils manquent, la version Ollama les télécharge.

## Installer l'application

**Étape 4. Lancer l'installation**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer le script d'installation. Il télécharge RAGFlow version 1.0.0, génère les mots de passe, démarre les six conteneurs et attend que tout réponde. Il peut être relancé sans risque.

```bash
outils/ragflow/installer.sh
```

*Résultat* : après une à deux minutes, les dernières lignes indiquent que l'application répond et que chaque service est en ordre :

```text
healthz (9380) : HTTP 200 après 38 s
{"db":"ok","redis":"ok","doc_engine":"ok","storage":"ok","message_queue":"ok","status":"ok"}
interface : HTTP 200
```

Chaque `"ok"` correspond à un service : base de données, mémoire tampon, moteur de recherche, stockage des fichiers, file d'attente.

## Créer le premier compte

RAGFlow n'a aucun compte au départ, et aucun modèle d'IA n'y est déclaré. Deux chemins mènent au même résultat : le script, qui fait tout d'un coup, ou l'interface, à la souris.

**Étape 5. Créer le compte et déclarer les modèles par le script**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer le script de configuration. Il crée un compte local fictif avec un mot de passe aléatoire, déclare les modèles de LLM-Service (réponse, recherche par le sens, transcription audio) et les choisit comme modèles par défaut.

```bash
python3 outils/ragflow/configurer.py
```

*Résultat* : chaque ligne se termine par `"message": "success"`. Le courriel et le mot de passe du compte sont rangés dans le fichier `donnees/IDENTIFIANTS-LOCAUX.txt`, à lire pour se connecter (chapitre 03). Ce script est écrit pour la version vLLM de LLM-Service ; avec la version Ollama, créer le compte à la souris (étape 6) et déclarer les modèles comme au chapitre 03.

**Étape 6. Ou créer le compte à la souris**
*Où* : navigateur Windows › `http://127.0.0.1:8088` › lien « Sign up » sous le formulaire de connexion.
La page de connexion est en anglais au premier lancement. Cliquer sur « Sign up », remplir l'adresse (pastille 1), le nom affiché (pastille 2) et le mot de passe (pastille 3), puis cliquer sur « Continue » (pastille 4).

![Formulaire de création du premier compte](../img/01-installation/01-inscription.png)
*Écran : page de connexion, formulaire « Create an account ».*

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Email » | adresse du compte, qui sert d'identifiant ; une adresse fictive suffit pour un compte local |
| 2 | « Nickname » | nom affiché dans l'interface |
| 3 | « Password » | mot de passe du compte (masqué sur la capture) |
| 4 | « Continue » | crée le compte |
| 5 | « Sign in » | revient au formulaire de connexion |

*Résultat* : le compte est créé ; la connexion se fait ensuite comme au chapitre 03. Les modèles restent à déclarer (chapitre 03, « Déclarer les modèles d'IA »).

## Vérifier, arrêter et redémarrer

**Étape 7. Voir l'état de l'application**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer :

```bash
outils/ragflow/etat.sh
```

*Résultat* : la liste des six conteneurs, chacun « Up » et la plupart « (healthy) », puis l'état des services et du service de modèles :

```text
santé : {"db":"ok","redis":"ok","doc_engine":"ok","storage":"ok","message_queue":"ok","status":"ok"}
interface : HTTP 200
LLM-Service : vllm-central en marche
LLM-Service : vllm-embed en marche
```

Seule l'application (`rag-ragflow-server`) est joignable, et seulement depuis ce poste : sa ligne montre `127.0.0.1:8088` pour l'interface et `127.0.0.1:9380` pour les programmes ; les cinq autres conteneurs n'ont aucune adresse ouverte.

**Étape 8. Arrêter RAGFlow**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer :

```bash
outils/ragflow/arreter.sh
```

*Résultat* : le message « RAGFlow arrêté. » s'affiche. Les bases, documents, assistants et comptes sont conservés ; LLM-Service, partagé, reste en marche.

**Étape 9. Redémarrer RAGFlow**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Vérifier que LLM-Service tourne (étape 3), puis lancer :

```bash
outils/ragflow/demarrer.sh
```

*Résultat* : après moins d'une minute, la ligne `"status":"ok"` puis l'adresse de l'interface s'affichent :

```text
RAGFlow : http://127.0.0.1:8088 (identifiants : donnees/IDENTIFIANTS-LOCAUX.txt)
```

## Désinstaller RAGFlow

**Étape 10. Tout supprimer**
*Où* : terminal Ubuntu, dossier `RAGFlow-Test-Bench`.
Lancer la commande ci-dessous. Elle annonce ce qu'elle va supprimer et demande une confirmation : taper `oui`. Toutes les bases, tous les documents et tous les comptes sont perdus : faire d'abord une sauvegarde si besoin (annexe [A4. Exploitation](../annexes/A4-exploitation.md)).

```bash
outils/communs/nettoyer.sh ragflow
```

*Résultat* : en une quinzaine de secondes, les conteneurs, leurs données et le dossier `donnees/ragflow/` sont supprimés, et le mot « Terminé. » s'affiche. Les images téléchargées restent sur le disque (environ 3 Go) pour une réinstallation rapide ; LLM-Service n'est pas touché.

## Bon à savoir

- Le cycle complet désinstaller, réinstaller, recréer le compte a été chronométré à moins d'une minute et demie, images déjà téléchargées.
- Aucun modèle n'est téléchargé à l'installation : les outils de lecture des documents (reconnaissance de caractères, mise en page, tableaux) sont livrés avec l'application.
- L'application occupe environ 3,7 Go de mémoire au repos et 5,4 Go pendant l'analyse de documents ; 3,1 Go d'images et 1,2 Go de données sur le disque juste après l'installation.
- Aucune version plus récente que la 1.0.0 n'existait au moment des essais. Avant toute mise à jour, faire une sauvegarde : le passage d'une ancienne version à la 1.0 transforme la base de données sans retour possible.
- Le détail technique de l'installation (fichiers de configuration, adresses, mémoire par conteneur) est dans l'annexe [A4. Exploitation](../annexes/A4-exploitation.md).

## En cas de problème

| Symptôme | Cause | Que faire |
|---|---|---|
| Le moteur de recherche ne démarre pas, l'installation attend sans fin | réglage `vm.max_map_count` trop bas (étape 2) | le relever dans la machine virtuelle de Docker ; ce réglage sort du cadre de ce manuel |
| Le script de désinstallation s'arrête aussitôt (code 126) | les scripts ont perdu leur droit d'exécution, par exemple après extraction d'une archive | lancer `chmod +x outils/communs/*.sh outils/ragflow/*.sh`, puis recommencer |
| Le port 8088 est déjà pris par un autre programme | conflit d'adresse | changer `SVR_WEB_HTTP_PORT` dans `donnees/ragflow/ragflow.env`, puis redémarrer |
| La connexion dans le navigateur est refusée (« email and password do not match ») alors que le compte existe | compte créé par un programme qui a envoyé le mot de passe sous une autre forme | recréer le compte avec le script de l'étape 5 ou à la souris (étape 6) |

Les autres problèmes sont traités au chapitre [15. En cas de problème](15-en-cas-de-probleme.md).

---
*Version décrite : RAGFlow v1.0.0, essais des 9 et 11 novembre 2026. Détails et preuves : [rapport d'essais](../annexes/A6-rapport-d-essais.md).*
