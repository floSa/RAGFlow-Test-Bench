# 01. Découvrir RAGFlow

> Ce chapitre apprend à quoi sert RAGFlow, à qui il convient, ce qu'il sait faire et ce qu'il faut comme machine. Il donne aussi les mots de base employés dans tout le manuel.
> **Point de départ** : aucun écran ; ce chapitre se lit avant d'installer quoi que ce soit.
> **Durée** : environ 10 minutes de lecture. **Avant** : aucun.

## Ce qu'il faut savoir

RAGFlow est une application web qui répond à des questions posées sur ses propres documents. Chaque réponse indique, phrase par phrase, le passage et la page d'où vient l'information : on peut donc vérifier ce que dit l'outil. Exemple : à la question « Quel est le montant de la prime d'intéressement 2025 ? », RAGFlow répond « 1 150 euros par salarié, versée en avril 2026 » et renvoie au compte rendu de réunion qui le dit. L'application s'installe sur un poste ou un serveur ; avec des modèles d'IA installés sur la même machine, les documents ne la quittent jamais.

## Ce que fait RAGFlow

Le travail s'organise en **bases de connaissances**. Une base réunit des documents sur un même sujet : contrats, procédures, comptes rendus, tableaux, présentations. À l'arrivée, chaque document est lu (y compris un scan, grâce à la reconnaissance de caractères intégrée), découpé en passages, puis rangé pour la recherche.

Sur ces bases, RAGFlow propose :

- des **assistants de discussion**, qui répondent en citant leurs sources ;
- des **pages de recherche**, qui affichent les passages trouvés et un résumé ;
- des **agents**, enchaînements d'étapes dessinés à la souris (chercher, rédiger, envoyer) ;
- des **synthèses automatiques** : cartes mentales, graphes des personnes et des sociétés citées, frises chronologiques.

## Pour qui

RAGFlow convient bien :

- à une équipe ou un service qui interroge un fonds documentaire commun, avec un compte par personne ;
- à des documents difficiles : scans, tableaux, mises en page en colonnes ;
- à un besoin d'automatisation : tout ce que fait l'interface se pilote aussi par programme.

Il convient moins bien :

- à un poste modeste : l'application seule occupe plus de 5 Go de mémoire pendant l'ajout de documents, avant même les modèles d'IA ;
- à une personne qui cherche un outil très simple à installer et à régler ;
- à un usage tout en français sans retouche : plusieurs messages et modèles d'agents restent en anglais.

## Le projet

RAGFlow est un logiciel libre, publié sous licence Apache 2.0 : gratuit, usage commercial autorisé, aucun abonnement. Son code est sur GitHub (`infiniflow/ragflow`), son site est ragflow.io. Le projet, créé en décembre 2023, est très suivi (près de 94 000 étoiles sur GitHub) et très actif (plus de 900 contributeurs, près de 2 800 modifications sur les trois derniers mois). La version 1.0.0 décrite ici est parue le 6 novembre 2026.

## Ce que sait faire RAGFlow

Réponses : **Oui**, **Non**, ou **Partiel** avec la limite en une phrase.

| Fonction | Réponse |
|---|---|
| Utiliser des modèles d'IA installés sur la machine (Ollama, vLLM ou tout serveur compatible OpenAI) | Oui |
| Utiliser des services d'IA en ligne (OpenAI, Mistral, Google…) | Oui, plusieurs dizaines |
| Lire les PDF, Word, Excel, PowerPoint, texte, Markdown, pages HTML, courriels | Oui |
| Lire les tableaux en gardant lignes et colonnes | Oui |
| Lire un document scanné | Oui, avec quelques confusions de caractères à corriger à la main |
| Transcrire un fichier audio | Oui, avec un service de transcription installé à côté |
| Trier une seconde fois les passages trouvés (reranker) | Partiel : aucun modèle fourni, il faut un serveur qui en sert un ; essayé avec succès sur la machine d'essai |
| Lire une vidéo | Non |
| Lire une image seule | Partiel : il faut un modèle capable de lire les images |
| Lire les pages d'un site interne par son plan (sitemap) | Partiel : refusé par défaut pour une adresse privée |
| Converser avec une ou plusieurs bases | Oui |
| Chercher à la fois par les mots et par le sens, avec un réglage du poids de chacun | Oui |
| Citer le passage et la page de chaque information | Oui |
| Refuser de répondre quand l'information n'est pas dans les documents | Oui |
| Laisser le modèle mener lui-même plusieurs recherches (mode « Agentic ») | Partiel : plus lent et moins juste avec un petit modèle |
| Corriger à la main un passage mal lu | Partiel : possible sur la plupart des documents, défaut sur les PDF (chapitre 06) |
| Dessiner des agents à partir de modèles prêts à l'emploi | Oui, consignes en anglais |
| Produire cartes mentales, graphes et frises | Oui |
| Interface en français | Oui, par le menu de langue ; la page de connexion reste en anglais au premier lancement |
| Plusieurs utilisateurs, équipes, compte d'administration | Oui |
| Fonctionner sans connexion à Internet | Oui, avec des modèles installés sur la machine |
| Sauvegarder et restaurer | Oui, par copie des données, application arrêtée |

## Le matériel nécessaire

RAGFlow lui-même ne contient aucun modèle d'IA : il les appelle sur un service à part. La machine doit donc faire tourner les deux. Le détail des mesures est dans l'annexe [A2. Choisir son matériel et ses modèles](../annexes/A2-choisir-son-materiel-et-ses-modeles.md).

**Configuration minimale sans carte graphique** (calculée, pas essayée en entier avec RAGFlow) :

- processeur récent à 8 cœurs ;
- 16 Go de mémoire vive : un peu plus de 5 Go pour RAGFlow, environ 5 Go pour les modèles, le reste pour Windows ;
- 10 Go de disque libre ;
- un petit modèle de réponse de 4 milliards de paramètres (par exemple `qwen3:4b-instruct`, 2,5 Go) et le modèle `bge-m3` pour la recherche par le sens (1,2 Go) ;
- attente prévisible : 30 à 50 secondes par question, plusieurs minutes pour analyser une dizaine de documents.

**Configuration essayée, avec une carte graphique NVIDIA** :

- carte RTX 4060 Ti à 16 Go de mémoire graphique, dont un peu plus de 8 Go utilisés (8 Go devraient suffire) ;
- 32 Go de mémoire vive, dont environ 16 Go réellement utilisés ;
- service de modèles central : modèle de réponse Qwen3.5-4B (`chat`), modèle `bge-m3` pour la recherche par le sens (`embed`), reranker `bge-reranker-v2-m3` (`rerank`) sur la carte graphique, et modèle de transcription sur le processeur ;
- attente constatée : 8 secondes par question en médiane, jusqu'à une minute pour les plus longues, car ce modèle réfléchit avant de répondre (un peu plus d'une seconde avec le modèle Gemma 4 E4B des premiers essais, qui ne réfléchit pas) ; environ une minute pour analyser neuf documents.

Le nombre de documents d'une base n'est pas limité par le modèle : seuls les six à huit passages les plus proches de la question lui sont transmis. Il est limité par le temps d'analyse (environ une minute par mégaoctet de documents, cinq secondes par page scannée) et par la mémoire de la machine.

## Les résultats des essais en cinq lignes

Essais menés sur neuf documents d'une entreprise fictive (dont un contrat scanné, un message vocal et un rapport en anglais), avec 38 questions dont la réponse est connue :

- **justesse** : 33 bonnes réponses sur 34 avec les réglages d'origine, 34 sur 34 avec les réglages conseillés au chapitre 08 ou avec le reranker ;
- **honnêteté** : les 4 questions sans réponse dans les documents sont toutes refusées, sans invention ;
- **sources** : le bon document est cité dans les 34 cas, la bonne page dans tous les cas où il y a des pages ;
- **rapidité** : environ 8 secondes par réponse en médiane avec une carte graphique et le modèle `chat`, qui réfléchit avant de répondre ;
- **analyse** : les neuf documents sont prêts en une minute environ.

Détail : annexe [A1. Évaluation : qualité et performances](../annexes/A1-evaluation-qualite-et-performances.md).

## Les mots de base

- **RAG** (de l'anglais *retrieval-augmented generation*, génération augmentée par récupération) : la méthode qui donne son nom à RAGFlow. À chaque question, l'outil retrouve d'abord les passages utiles dans les documents, puis les donne au modèle d'IA, qui rédige sa réponse à partir d'eux et les cite. Le modèle répond ainsi sur les documents de l'entreprise, qu'il n'a jamais appris.
- **Document** : un fichier ajouté à RAGFlow (PDF, Word, tableur, page web, fichier audio…).
- **Base de connaissances** : un ensemble de documents interrogés ensemble, avec leur façon d'être lus. RAGFlow l'appelle aussi « dataset » à certains endroits.
- **Analyse** : l'étape où RAGFlow lit un document, le découpe et le range pour la recherche. Un document non analysé ne sert à rien.
- **Passage** : un morceau de document, de quelques lignes à une page, que RAGFlow retrouve et transmet au modèle. L'interface l'appelle « segment ».
- **Gabarit** : la façon de découper un type de document (texte suivi, tableur ligne par ligne, présentation diapositive par diapositive…). L'interface l'appelle « Mode d'analyse » ou « pipeline intégré ».
- **Modèle d'IA** : le programme qui rédige les réponses (« modèle de chat ») ou qui traduit le sens d'un texte en nombres pour la recherche (« modèle d'embedding »).
- **Recherche par les mots et par le sens** : RAGFlow retrouve un passage soit parce qu'il contient les mots de la question, soit parce qu'il en a le sens, même avec d'autres mots ; il combine les deux selon un poids réglable.
- **Question** : une phrase en langage courant posée à un assistant.
- **Assistant** : un interlocuteur relié à une ou plusieurs bases ; il cherche les passages utiles puis fait rédiger la réponse. L'interface le range sous « Discussion » et l'appelle « chat ».
- **Citation** : le petit numéro entre crochets (« [1] ») placé après une phrase de la réponse ; il renvoie au passage qui la justifie.
- **Jeton** : l'unité dans laquelle un modèle compte le texte, à peu près une syllabe ; l'interface affiche le nombre de jetons consommés par chaque réponse.
- **Agent** : un enchaînement d'étapes dessiné à la souris (chercher, rédiger, mettre en forme), plus libre qu'un assistant.

Ces mots et les autres termes techniques sont repris dans le [glossaire](16-glossaire.md).

## Bon à savoir

- RAGFlow ne connaît que ce qui est dans ses bases : il ne remplace pas une recherche sur Internet.
- Une réponse citée se vérifie en deux secondes : survoler le numéro affiche le passage d'origine. C'est l'habitude à prendre.
- Le parcours le plus court, de l'installation à la première réponse, tient dans les chapitres 02 à 04.

## En cas de problème

| Symptôme | Cause | Que faire |
|---|---|---|
| La machine n'a que 8 Go de mémoire | RAGFlow et les modèles n'y tiennent pas ensemble | utiliser une machine plus grande ou des modèles en ligne ; voir l'annexe A2 |
| Les documents ne doivent pas quitter le poste | les modèles en ligne reçoivent les passages | déclarer uniquement des modèles installés sur la machine (chapitre 03) |

Les autres problèmes sont traités au chapitre [15. En cas de problème](15-en-cas-de-probleme.md).

---
*Version décrite : RAGFlow v1.0.0, essais des 9, 11 et 12 novembre 2026. Détails et preuves : [rapport d'essais](../annexes/A6-rapport-d-essais.md).*
