# RAGFlow en bref

Version 1.0.0, essayée le 9 novembre 2026 sur Windows 11 (WSL2), avec des modèles d'IA installés sur la machine.

## Sommaire

1. [Ce que c'est](#1-ce-que-cest)
2. [Pour qui](#2-pour-qui)
3. [Le projet](#3-le-projet)
4. [Fonctions](#4-fonctions)
5. [Matériel nécessaire](#5-matériel-nécessaire)
6. [Résultats mesurés](#6-résultats-mesurés)
7. [Pour aller plus loin](#7-pour-aller-plus-loin)

## 1. Ce que c'est

RAGFlow est une application web qui répond à des questions sur ses propres documents et indique, pour chaque phrase de la réponse, le passage et la page d'où elle vient.

Le travail s'organise en **bases de connaissances**. Chaque document y est lu (y compris les scans, grâce à une reconnaissance de caractères intégrée), découpé en passages, puis indexé pour la recherche par mots et par le sens.

Sur ces bases, on crée des **assistants de conversation**, des **agents** (enchaînements d'étapes dessinés à la souris) et des **synthèses automatiques** : cartes mentales, graphes de connaissances, frises.

L'application s'installe sur un poste ou un serveur. Elle peut fonctionner sans aucun service en ligne : les modèles d'IA tournent alors sur la même machine, et les documents ne quittent pas le poste.

## 2. Pour qui

| Adapté | Peu adapté |
|---|---|
| Une équipe ou un service qui interroge un fonds documentaire commun, avec des comptes séparés | Un poste modeste : l'application seule demande 3,6 à 5,3 Gio de mémoire, avant les modèles d'IA |
| Des documents difficiles : scans, tableaux, mises en page complexes | Une personne qui veut un outil très simple à installer et à régler |
| Un besoin d'automatisation : tout se pilote par une API et un module Python | Des usages en français sans retouche : plusieurs messages et modèles d'agents sont en anglais |

## 3. Le projet

| | |
|---|---|
| Dépôt | https://github.com/infiniflow/ragflow |
| Site | https://ragflow.io |
| Licence | Apache-2.0 : libre, usage commercial autorisé |
| Popularité | 93 880 étoiles, 11 278 forks sur GitHub |
| Activité | très forte : 2 763 modifications sur les 90 derniers jours, 925 contributeurs |
| Ancienneté | projet créé en décembre 2023 ; version 1.0.0 publiée le 6 novembre 2026, réécrite en Go |
| Coût | gratuit ; aucun abonnement |

Chiffres relevés sur GitHub le 9 novembre 2026.

## 4. Fonctions

Réponses : **Oui**, **Non**, ou **Partiel** avec la limite en une phrase.

### Modèles d'IA

| Fonction | Réponse |
|---|---|
| Modèles installés sur la machine avec Ollama | Oui |
| Modèles installés sur la machine avec vLLM ou tout serveur compatible OpenAI | Oui (utilisé pour ces essais) |
| Services en ligne (OpenAI, Anthropic, Mistral, Google…) | Oui, plusieurs dizaines |
| Calcul des embeddings sur la machine (représentation numérique du sens d'un passage, qui sert à la recherche par le sens) | Oui |
| Reranking (second tri des passages trouvés, par un modèle spécialisé) | Partiel : prévu, mais aucun modèle fourni ; il faut un service séparé |
| Transcription audio sur la machine | Oui, avec un serveur de voix séparé |

### Documents acceptés

| Fonction | Réponse |
|---|---|
| PDF, Word, Excel, PowerPoint, texte, Markdown, HTML, courriels, EPUB | Oui |
| Tableaux | Oui, restitués en lignes et colonnes |
| Documents scannés (reconnaissance de caractères) | Oui, environ 5 secondes par page ; quelques confusions de caractères à corriger à la main |
| Pages d'un site web, par son plan (sitemap) | Partiel : refusé pour un site interne, sauf réglage qui affaiblit la sécurité |
| Audio | Oui, transcrit automatiquement |
| Vidéo | Non |
| Images seules | Partiel : demande un modèle d'IA capable de lire les images, non essayé |

### Recherche et réponses

| Fonction | Réponse |
|---|---|
| Conversation sur une ou plusieurs bases | Oui |
| Recherche combinant mots et sens, avec réglage du poids de chacun | Oui |
| Indication de la source dans la réponse | Oui, passage par passage |
| Indication de la page | Oui, avec la position du passage dans le document |
| Refus de répondre quand l'information n'est pas dans les documents | Oui |
| Mode « agentique » (le modèle mène lui-même plusieurs recherches) | Partiel : plus lent et moins juste avec un petit modèle |
| Correction manuelle d'un passage mal lu | Oui |

### Production

| Fonction | Réponse |
|---|---|
| Agents dessinés à partir de modèles prêts à l'emploi | Oui, 19 modèles ; consignes en anglais |
| Cartes mentales et graphes de connaissances tirés des documents | Oui |
| Wikis, frises, tables des matières automatiques | Prévu, non essayé |

### Installation et exploitation

| Fonction | Réponse |
|---|---|
| Installation | Docker, six conteneurs : l'application, un moteur de recherche, une base de données, un stockage de fichiers, un cache, une file de tâches |
| Mémoire nécessaire, hors modèles d'IA | 3,6 Gio au repos, 5,3 Gio pendant l'ajout de documents |
| Interface en français | Oui, par le sélecteur de langue ; la page de connexion reste en anglais |
| Plusieurs utilisateurs avec leurs propres comptes | Oui, avec équipes et compte d'administration |
| API pour automatiser | Oui, complète ; le module Python a deux défauts contournés dans ces manuels |
| Fonctionnement hors ligne | Oui en principe : aucun téléchargement mentionné dans le journal du serveur ; le trafic réseau n'a pas été enregistré |
| Sauvegarde et restauration | Oui, par copie des données, application arrêtée (une demi-minute) |

## 5. Matériel nécessaire

### Sans carte graphique : configuration minimale, estimée

| Élément | Minimum |
|---|---|
| Processeur | 8 cœurs récents ; 8 fils de calcul réservés au modèle |
| Mémoire vive | 16 Go : application 5,3 Gio en pointe, modèles 5 Go environ avec un contexte de 4 096 jetons, le reste pour Windows |
| Disque libre | 10 Go : application 3,1 Go, données 1,2 Go à vide, modèles environ 4 Go |
| Modèle de réponse | qwen3:4b-instruct : 4 milliards de paramètres, 2,5 Go |
| Modèle d'embedding | bge-m3 : 1,2 Go, multilingue |
| Taille de contexte | 4 096 jetons (16 384 demandent trop de mémoire sur ce profil) |

Temps d'attente attendu : 30 à 50 secondes par question, le temps que le modèle lise les consignes et les passages retrouvés (1 800 à 3 300 jetons). L'ajout de documents prend plusieurs minutes pour une dizaine de documents. Ces valeurs sont calculées à partir des mesures du service de modèles sur un portable sans carte graphique, pas mesurées avec RAGFlow.

**Combien de documents.** Seuls les 6 à 8 passages les plus proches de la question sont transmis au modèle : le nombre de documents d'une base n'est pas limité par le modèle, mais par le temps d'ajout (environ 1 minute par mégaoctet de documents, et 5 secondes par page scannée) et par la mémoire du moteur de recherche.

### Avec une carte graphique NVIDIA : configuration mesurée

| Élément | Valeur |
|---|---|
| Carte graphique | RTX 4060 Ti 16 Go (15,2 Go occupés par les deux modèles, dont 80 % réservés par le modèle de réponse) ; 12 Go estimés suffisants |
| Mémoire vive | 32 Go installés ; environ 16 Gio utilisés (application 5,3 Gio, service de modèles 10,6 Gio) |
| Modèle de réponse | Gemma 4 E4B en version 4 bits, sur vLLM |
| Modèle d'embedding | bge-m3, sur vLLM |
| Taille de contexte | 16 384 jetons déclarés ; 4 096 suffisent, 3 072 ne suffisent plus |
| Temps d'attente | 1,3 seconde par question ; ajout des 9 documents en moins d'une minute |

**Modèles plus légers.** Aucun modèle de moins de 3 milliards de paramètres n'a été essayé : le service de modèles est partagé avec d'autres applications.

## 6. Résultats mesurés

Test sur 38 questions dont la réponse est connue, posées à 9 documents d'une entreprise fictive (dont un contrat scanné, un fichier audio et un document en anglais). Modèle Gemma 4 E4B sur carte graphique.

| Mesure | Résultat |
|---|---|
| Réponses justes | 33 sur 34 avec les réglages d'origine ; 34 sur 34 en donnant plus de poids à la recherche par le sens |
| Questions sans réponse dans les documents | 4 refus sur 4, aucune réponse inventée |
| Bonne source et bonne page | bon document dans les 34 cas, bonne page dans 24 cas sur 24 |
| Temps de réponse | 1,3 seconde en général, moins de 2 secondes dans 95 % des cas |
| Ajout des 9 documents | moins d'une minute |

Détail : [Qualité et performances](12-qualite-et-performances.md).

## 7. Pour aller plus loin

| Pour | Lire |
|---|---|
| Installer | [01. Installation](01-installation.md) |
| Première base, première réponse | [02. Prise en main](02-prise-en-main.md) |
| Deux cas d'usage complets | [11. Recettes](11-recettes.md) |
| Limites connues et questions en suspens | [index, « Ce qui reste ouvert »](README.md#ce-qui-reste-ouvert) |

Les réponses de cette page viennent des essais du 9 novembre 2026 et du code source de la version 1.0.0 : [relevé GitHub](../../outils/resultats/ragflow/identite-github-2026-11-09.json), [relecture du code](../../outils/resultats/ragflow/relecture.md), [résultats des essais](../../outils/resultats/ragflow/).
