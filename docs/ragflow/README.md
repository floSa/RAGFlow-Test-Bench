# RAGFlow — manuel utilisateur

Ce manuel apprend à installer et à utiliser RAGFlow, une application qui répond aux questions posées sur ses propres documents en citant ses sources ; il s'adresse à une personne qui n'a jamais vu le logiciel, à l'aise avec un terminal mais pas forcément développeur, et se lit dans l'ordre.

| Version décrite | Date des essais | Machine | Langue de l'interface |
|---|---|---|---|
| RAGFlow v1.0.0 | 9 et 11 novembre 2026 | Windows 11 + WSL2, Ryzen 5 9600X, 32 Go de mémoire, carte graphique RTX 4060 Ti 16 Go ; modèles d'IA installés sur la machine | français, par le menu de langue (page de connexion en anglais au premier lancement) |

## Par où commencer

Les quatre premiers chapitres mènent, en une heure environ, de rien à une première réponse citée :

1. [Découvrir RAGFlow](manuel/01-decouvrir-ragflow.md) : savoir si l'outil convient et ce qu'il faut comme machine.
2. [Installer RAGFlow](manuel/02-installer-ragflow.md) : l'installer, le démarrer, l'arrêter.
3. [Premiers pas](manuel/03-premiers-pas.md) : se connecter et se repérer.
4. [Première question en dix minutes](manuel/04-premiere-question.md) : obtenir une première réponse citée.

## Partie 1 — Manuel utilisateur

| N° | Chapitre | Ce qu'on saura faire |
|---|---|---|
| 01 | [Découvrir RAGFlow](manuel/01-decouvrir-ragflow.md) | dire à quoi sert RAGFlow, pour qui, avec quelle machine, et employer les mots de base (document, base, passage, citation) |
| 02 | [Installer RAGFlow](manuel/02-installer-ragflow.md) | installer RAGFlow sous Windows 11 et WSL2 face à un serveur de modèles existant, créer le premier compte, le démarrer, l'arrêter et le désinstaller |
| 03 | [Premiers pas](manuel/03-premiers-pas.md) | se connecter, passer l'interface en français, reconnaître chaque zone de l'écran, distinguer les modèles à brancher des traitements intégrés (DeepDoc, moteur de recherche) et brancher les modèles d'un serveur existant |
| 04 | [Première question en dix minutes](manuel/04-premiere-question.md) | créer une base, y analyser deux documents, créer un assistant et vérifier la source de sa réponse |
| 05 | [Ajouter et organiser ses documents](manuel/05-ajouter-et-organiser-ses-documents.md) | ajouter, renommer, écarter, supprimer et réanalyser des fichiers, leur donner des métadonnées, suivre les analyses et partager un fichier entre bases |
| 06 | [Régler la lecture des documents](manuel/06-regler-la-lecture-des-documents.md) | choisir le bon gabarit de découpage, régler une base, contrôler la lecture d'un scan et corriger un passage mal lu |
| 07 | [Poser des questions et lire les sources](manuel/07-poser-des-questions-et-lire-les-sources.md) | converser, vérifier chaque source, reconnaître un refus, choisir entre « Naive » et « Agentic », comparer des modèles, publier un assistant |
| 08 | [Régler un assistant](manuel/08-regler-un-assistant.md) | comprendre chaque réglage d'un assistant, appliquer les réglages conseillés et tester la recherche sans le modèle |
| 09 | [Rechercher dans ses documents](manuel/09-rechercher.md) | créer une page de recherche avec résumé, passages et carte mentale, et l'intégrer dans un site |
| 10 | [Construire un agent](manuel/10-agents.md) | créer un agent à partir d'un modèle prêt à l'emploi, l'essayer, le publier et lui donner une mémoire |
| 11 | [Produire des synthèses automatiques](manuel/11-syntheses-automatiques.md) | faire produire graphes, arbres, frises et cartes mentales à partir des documents d'une base |
| 12 | [Alimenter une base depuis une source externe](manuel/12-sources-externes.md) | relier une base à une source de données pour qu'elle se remplisse seule, et lire le journal de synchronisation |
| 13 | [Gérer son compte, son équipe et ses clés](manuel/13-comptes-equipe-et-cles.md) | inviter des collègues, régler son profil, créer et supprimer une clé d'accès pour les programmes |
| 14 | [Cas pratiques](manuel/14-cas-pratiques.md) | mettre en place de bout en bout un assistant documentaire d'entreprise et une base mise à jour chaque jour |
| 15 | [En cas de problème](manuel/15-en-cas-de-probleme.md) | reconnaître un message d'erreur, en trouver la cause et appliquer le remède |
| 16 | [Glossaire](manuel/16-glossaire.md) | retrouver la définition simple de chaque terme employé |

## Partie 2 — Évaluation et compléments

| Annexe | Contenu |
|---|---|
| [A1. Évaluation : qualité et performances](annexes/A1-evaluation-qualite-et-performances.md) | résultats du banc de 38 questions, réglages qui changent le résultat, préconisations |
| [A2. Choisir son matériel et ses modèles](annexes/A2-choisir-son-materiel-et-ses-modeles.md) | configurations minimales sans et avec carte graphique, taille de contexte, temps d'attente |
| [A3. Automatiser par l'API](annexes/A3-automatiser-par-l-api.md) | API HTTP et module Python, exemples exécutés, défauts contournés |
| [A4. Exploitation](annexes/A4-exploitation.md) | installation détaillée, sauvegarde et restauration, mise à jour, journaux, sécurité, administration |
| [A5. Fonctionnement interne](annexes/A5-fonctionnement-interne.md) | RAG, architecture, services, ports, modèles, DeepDoc |
| [A6. Rapport d'essais](annexes/A6-rapport-d-essais.md) | méthode, preuves, étiquettes, renvois aux résultats bruts |
| [Carte de l'interface](annexes/carte-interface.md) | chaque page, menu et réglage de l'interface, avec le chapitre qui le décrit |

## Parcours conseillés

| Besoin | Parcours |
|---|---|
| Essayer en une heure | chapitres [01](manuel/01-decouvrir-ragflow.md) à [04](manuel/04-premiere-question.md) |
| Mettre en service pour une équipe | chapitres [05](manuel/05-ajouter-et-organiser-ses-documents.md) à [08](manuel/08-regler-un-assistant.md), puis [13](manuel/13-comptes-equipe-et-cles.md) et [14](manuel/14-cas-pratiques.md) |
| Améliorer les réponses | chapitres [06](manuel/06-regler-la-lecture-des-documents.md) et [08](manuel/08-regler-un-assistant.md), annexe [A1](annexes/A1-evaluation-qualite-et-performances.md) |
| Choisir une machine | chapitre [01](manuel/01-decouvrir-ragflow.md), annexe [A2](annexes/A2-choisir-son-materiel-et-ses-modeles.md) |
| Automatiser et exploiter | annexes [A3](annexes/A3-automatiser-par-l-api.md), [A4](annexes/A4-exploitation.md) et [A5](annexes/A5-fonctionnement-interne.md) |

## Limites connues

- Correction d'un passage tiré d'un PDF : « Confirmer » reste sans effet ; contournement au chapitre [06](manuel/06-regler-la-lecture-des-documents.md).
- Mode « Agentic » moins juste et plus lent que la réponse directe avec le petit modèle des essais (chapitre [07](manuel/07-poser-des-questions-et-lire-les-sources.md)).
- Aucun modèle de second tri des passages (reranker) dans le socle : non essayé.
- Module Python `ragflow-sdk` 1.0.0 : deux défauts, contournés dans l'annexe [A3](annexes/A3-automatiser-par-l-api.md).

Ce qui reste ouvert (sujets non traités, estimations, décisions en attente, relectures) est suivi dans le [rapport de fin de mission](../../RAPPORT-ragflow.md#11-ce-qui-reste-ouvert).
