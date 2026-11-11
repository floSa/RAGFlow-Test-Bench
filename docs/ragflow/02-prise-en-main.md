# 02. Prise en main

> **Objet** : de zéro à la première réponse citée, tout à la souris dans l'interface web : se connecter, passer en français, créer une base de connaissances, importer et analyser des fichiers, lire les passages, créer un assistant, poser une question, lire les citations.
> **Prérequis** : [notions fondamentales](00-notions-fondamentales.md) (visite de l'interface), [installation](01-installation.md) (compte créé, modèles par défaut déclarés).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré les 9 et 11 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : documents fictifs de l'entreprise Vélanor (`corpus/documents/`) ; identifiants locaux dans `donnees/IDENTIFIANTS-LOCAUX.txt`, mot de passe masqué sur les captures ; la base « Manuel-Prise-en-main » et l'assistant « Manuel-Assistant » sont créés par le scénario de captures puis supprimés (`outils/ragflow/nettoyer_manuel.py`).

Toutes les captures de ce manuel viennent d'un seul passage du scénario `prise_en_main` de `outils/ragflow/captures/captures.py`, qui fait chaque geste à la souris, dans l'ordre des étapes. Le texte de chaque page capturée et la liste de ses éléments visibles sont dans `outils/resultats/ragflow/captures/02-prise-en-main/` (même nom que l'image), le déroulé dans `scenario.log`. [Vérifié]

## Sommaire

1. [Se connecter et passer l'interface en français](#1-se-connecter-et-passer-linterface-en-français)
2. [Créer une base de connaissances](#2-créer-une-base-de-connaissances)
3. [Importer des fichiers](#3-importer-des-fichiers)
4. [Lancer l'analyse et lire les passages](#4-lancer-lanalyse-et-lire-les-passages)
5. [Créer un assistant et le relier à la base](#5-créer-un-assistant-et-le-relier-à-la-base)
6. [Poser une question et lire les citations](#6-poser-une-question-et-lire-les-citations)
7. [Dépannage](#dépannage)
8. [Sources](#sources)

## 1. Se connecter et passer l'interface en français

### Essentiel

But : ouvrir une session et afficher l'interface en français.

1. Ouvrir `http://127.0.0.1:8088` dans le navigateur Windows. Saisir le courriel et le mot de passe du compte local (`donnees/IDENTIFIANTS-LOCAUX.txt`), puis cliquer sur « Sign in ».

![Page de connexion](img/02-prise-en-main/01-connexion.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Email » | courriel du compte, ici `banc.demo@exemple.fr` |
| 2 | « Password » | mot de passe (masqué sur la capture) |
| 3 | « Remember me » | case de mémorisation de la connexion (laissée décochée) |
| 4 | « Sign in » | ouvre la session et affiche l'accueil |

2. L'accueil s'affiche en anglais. Cliquer sur « English » dans l'en-tête, puis sur « Français ».

![Menu de langue](img/02-prise-en-main/02-choix-langue.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « English » | menu de langue, à droite de l'en-tête |
| 2 | « Français » | passe toute l'interface en français |

3. L'interface est en français. La barre du haut donne accès à chaque fonction (détail dans la visite du manuel [00](00-notions-fondamentales.md)).

![Accueil en français](img/02-prise-en-main/03-accueil.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Base de connaissances » | bases de documents (sections 2 à 4) |
| 2 | « Discussion » | assistants de chat (sections 5 et 6) |
| 3 | « Français » | langue choisie, modifiable à tout moment |

### Pour aller plus loin

La page de connexion reste en anglais : la langue est mémorisée par le navigateur (stockage local, clé `lng`), pas par le compte. Changer la langue du compte par l'API (`PATCH /api/v1/users/me`) ne traduit pas l'interface au chargement ; seul le menu de l'en-tête le fait. [Vérifié] (`web/src/locales/config.ts` au tag v1.0.0 ; essais des captures)

## 2. Créer une base de connaissances

### Essentiel

But : créer une base vide qui recevra les documents. Une base regroupe des fichiers, la façon de les découper et le modèle d'embedding qui les vectorise.

1. Cliquer sur « Base de connaissances » dans la barre du haut, puis sur « Créer une base de connaissances ».

![Liste des bases de connaissances](img/02-prise-en-main/04-bases-de-connaissances.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Créer une base de connaissances » | ouvre la fenêtre de création |
| 2 | « Rechercher » | filtre les bases par nom |
| 3 | carte d'une base | nom, nombre de fichiers, date ; un clic ouvre la base |

2. Saisir un nom, garder le modèle d'embedding et le gabarit proposés, puis cliquer sur « Enregistrer ».

![Fenêtre de création d'une base](img/02-prise-en-main/05-creation-base.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom » | nom de la base, ici « Manuel-Prise-en-main » |
| 2 | « Modèle d'embedding » | modèle qui vectorise les passages, ici `bge-m3` de l'instance `llm-service-embed` (modèle par défaut, voir [01](01-installation.md)) |
| 3 | « General (built in) » | gabarit de découpage ; « General » convient à la plupart des documents (autres gabarits : manuel [03](03-datasets-et-decoupage.md)) |
| 4 | « Enregistrer » | crée la base et l'ouvre |

3. La base s'ouvre sur son onglet « Fichiers », vide.

![Base vide](img/02-prise-en-main/06-base-vide.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Manuel-Prise-en-main » | nom de la base ouverte, avec son nombre de fichiers et sa date |
| 2 | « Fichiers » | onglet des documents de la base ; les onglets suivants (« Test de récupération », « Journaux », « Configuration », « Artifacts ») sont décrits dans les manuels [03](03-datasets-et-decoupage.md), [05](05-assistants-et-citations.md) et [07](07-knowledge-compilation.md) |
| 3 | « Ajouter un fichier » | ouvre le menu d'ajout (section 3) |

### Pour aller plus loin

Le modèle d'embedding et le gabarit de découpage restent modifiables ensuite dans l'onglet « Configuration » de la base, décrit au manuel [03](03-datasets-et-decoupage.md). [Vérifié] (`outils/resultats/ragflow/captures/carte/09-base-configuration.txt`)

## 3. Importer des fichiers

### Essentiel

But : envoyer des documents dans la base. L'exemple importe deux documents courts du corpus : le compte rendu du CSE (`cse-2025-10-14.md`, 548 octets) et la FAQ du service après-vente (`faq-sav.html`, 810 octets).

1. Cliquer sur « Ajouter un fichier », puis sur « Téléverser un fichier ».

![Menu Ajouter un fichier](img/02-prise-en-main/07-menu-ajout.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Téléverser un fichier » | envoie des fichiers ou un dossier depuis le poste |
| 2 | « Créer un fichier vide » | crée un document vide (manuel [03](03-datasets-et-decoupage.md)) |

2. Glisser les fichiers dans la zone de dépôt, ou cliquer dessus pour les choisir ; ils s'affichent en liste. Laisser « Analyser à la création » désactivé pour lancer l'analyse à la main (section 4), puis cliquer sur « Enregistrer ».

![Fenêtre Téléverser un fichier](img/02-prise-en-main/08-televersement.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Analyser à la création » | activé, l'analyse démarre dès le téléversement ; désactivé ici |
| 2 | « Fichiers », « Dossier » | choisir des fichiers un par un, ou un dossier entier |
| 3 | zone de dépôt | glisser-déposer ou clic pour parcourir ; jusqu'à 32 fichiers et 1 Go par envoi en local, d'après le texte affiché |
| 4 | fichier choisi | nom et taille ; la corbeille le retire de l'envoi |
| 5 | « Enregistrer » | téléverse les fichiers dans la base |

3. Les fichiers apparaissent dans le tableau, avec 0 segment : ils ne sont pas encore analysés.

![Fichiers importés, pas encore analysés](img/02-prise-en-main/09-fichiers-importes.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | triangle de lancement | lance l'analyse de ce fichier (section 4) |
| 2 | « Nombre de segments » | nombre de passages produits ; 0 tant que l'analyse n'a pas tourné |
| 3 | « Activé » | active ou désactive le fichier |
| 4 | « General » | gabarit de découpage appliqué à ce fichier |

## 4. Lancer l'analyse et lire les passages

### Essentiel

But : découper chaque fichier en passages et les vectoriser, pour qu'ils puissent être retrouvés.

1. Cliquer sur le triangle de lancement de chaque fichier. Pendant l'analyse, l'état de la tâche s'affiche à côté du gabarit.

![Analyse en attente](img/02-prise-en-main/10-analyse-en-cours.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « En attente » | tâche d'analyse en file d'attente |
| 2 | « Cancel parsing tasks » | annule les analyses en cours |

2. Attendre que « Nombre de segments » se remplisse. Pour les deux fichiers de l'exemple, l'analyse a duré moins de 7 s (relevé de la page toutes les 3 s environ) : 4 passages pour le compte rendu, 1 pour la FAQ. [Vérifié] (`outils/resultats/ragflow/captures/02-prise-en-main/scenario.log`)

![Analyse terminée](img/02-prise-en-main/11-analyse-terminee.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nombre de segments » de `cse-2025-10-14.md` | 4 passages produits |
| 2 | « Nombre de segments » de `faq-sav.html` | 1 passage produit |
| 3 | icône d'état | analyse terminée ; un clic relance l'analyse, après une confirmation qui annonce la suppression des passages existants [Source] (`web/src/locales/fr.ts`, clé `redo`) |
| 4 | « cse-2025-10-14.md » | nom du fichier ; un clic ouvre ses passages |

3. Cliquer sur le nom d'un fichier : la page « Résultat du segment » montre le document à gauche et ses passages à droite, tels qu'ils seront retrouvés.

![Passages du compte rendu du CSE](img/02-prise-en-main/12-passages.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Aperçu » | aperçu du document d'origine ; « Artifact », à côté, est décrit au manuel [07](07-knowledge-compilation.md) |
| 2 | passage | texte d'un passage ; ici le découpage suit les titres Markdown |
| 3 | interrupteur du passage | active ou désactive le passage |
| 4 | « Texte complet », « Ellipse » | affiche les passages en entier ou abrégés |
| 5 | « + » | ajoute un passage (manuel [04](04-deepdoc.md)) |
| 6 | « Retour » | revient à la liste des fichiers |

### Pour aller plus loin

- Durée sur le corpus complet : les 9 documents (1 Mo) donnent 26 passages en 52 à 56 s, OCR du PDF scanné compris. [Vérifié] (`outils/resultats/ragflow/demo-2026-11-09.log`, `outils/resultats/ragflow/banc-2026-11-09-defaut.json`)
- Même dans une base réglée sur « General », RAGFlow choisit un gabarit adapté pour certains formats : la présentation `strategie-2026.pptx` apparaît avec le gabarit « Presentation », le fichier audio avec « Audio ». [Vérifié] (`outils/resultats/ragflow/captures/carte/05-base-fichiers.txt`)
- Le bandeau « Veuillez attendre la fin de l'analyse de vos fichiers avant de démarrer une discussion avec l'IA. » est justifié : un assistant ne peut pas être relié à une base dont aucun document n'a de passage (« doesn't own parsed file »). [Vérifié] (`outils/resultats/ragflow/installation-2026-11-09-verif-essai1.log`)
- Pour un PDF scanné, la lecture des passages montre la qualité de l'OCR ; voir le manuel [04](04-deepdoc.md).

## 5. Créer un assistant et le relier à la base

### Essentiel

But : créer un assistant de chat qui répond à partir des passages de la base.

1. Cliquer sur « Discussion » dans la barre du haut, puis sur « Créer un chat ».

![Liste des assistants](img/02-prise-en-main/13-discussions.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Créer un chat » | ouvre la fenêtre de création d'un assistant |
| 2 | carte d'un assistant | assistant existant (ici celui du jeu de démonstration) ; un clic l'ouvre |

2. Saisir un nom, puis cliquer sur « Enregistrer ».

![Fenêtre Créer un chat](img/02-prise-en-main/14-creation-assistant.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Nom » | nom de l'assistant, ici « Manuel-Assistant » |
| 2 | « Enregistrer » | crée l'assistant |

3. L'assistant apparaît dans la liste. Cliquer sur sa carte.

![Assistant créé](img/02-prise-en-main/15-assistant-cree.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Manuel-Assistant » | nouvel assistant, encore relié à aucune base |

4. La page de l'assistant s'ouvre sur une « Nouvelle conversation ». Cliquer sur l'engrenage, en haut à droite, pour ouvrir ses paramètres.

![Page de l'assistant](img/02-prise-en-main/16-page-assistant.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | engrenage | ouvre le panneau « Paramètres du chat » |

5. Le panneau « Paramètres du chat » s'ouvre à droite. Cliquer sur la liste « Bases de connaissances ».

![Paramètres du chat](img/02-prise-en-main/17-parametres-du-chat.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Paramètres du chat » | panneau de réglage de l'assistant ; l'icône à droite le referme |
| 2 | « Modèle » | modèle qui rédige les réponses, par défaut le modèle de chat déclaré (`gemma4:e4b`) |
| 3 | « Message d'accueil » | premier message affiché dans chaque conversation |
| 4 | « Bases de connaissances » | bases interrogées par l'assistant ; vide à la création |
| 5 | « Enregistrer » | enregistre les paramètres |

6. Cocher la base « Manuel-Prise-en-main » dans la liste.

![Choix de la base](img/02-prise-en-main/18-choix-base.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Rechercher... » | filtre les bases par nom |
| 2 | « Manuel-Prise-en-main » | base à relier ; la ligne rappelle son propriétaire et son modèle d'embedding (`bge-m3@llm-service-embed@VLLM`) |

7. La base apparaît dans le champ. Cliquer sur « Enregistrer » : le message « Modifié » confirme l'enregistrement. [Vérifié] (`outils/resultats/ragflow/captures/02-prise-en-main/scenario.log`)

![Base choisie](img/02-prise-en-main/19-base-choisie.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « Manuel-Prise-en-main » | base reliée ; la croix la retire |
| 2 | « Enregistrer » | enregistre l'assistant avec sa base |

### Pour aller plus loin

« Paramètres du modèle » (température, longueur de réponse, réflexion) et « Paramètres avancés » (citations, synthèse vocale, recherche web, métadonnées, mode de réponse) sont décrits dans les manuels [05](05-assistants-et-citations.md) et [06](06-agentic-rag.md). Par défaut, un assistant garde les 6 meilleurs passages, avec un poids de 0,7 pour les mots-clés et 0,3 pour les vecteurs. [Vérifié] (`outils/resultats/ragflow/banc-2026-11-09-defaut.json`)

## 6. Poser une question et lire les citations

### Essentiel

But : interroger l'assistant et vérifier sur quels passages s'appuie la réponse.

1. Taper la question dans la zone de saisie, puis cliquer sur l'avion en papier (« Send message »).

![Question saisie](img/02-prise-en-main/20-question.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | « + » à côté de « Conversations » | ouvre une nouvelle conversation |
| 2 | zone « Saisissez votre message ici... » | question, ici « Quel est le montant de la prime d'intéressement 2025 ? » |
| 3 | « Naive » | mode de réponse directe ; l'autre mode, « Agentic », est comparé au manuel [06](06-agentic-rag.md) |
| 4 | « Send message » | envoie la question |

L'envoi de cette question à « Manuel-Assistant » n'a pas pu être fait le 11 novembre 2026 : le serveur de chat de LLM-Service (`vllm-central`) redémarrait en boucle, faute de mémoire GPU libre. L'étape est [À tester] pour cet assistant. La réponse attendue d'après le corpus est 1 150 euros par salarié (question Q27, `corpus/questions.json`), passage visible à l'étape 3 de la section 4.

2. La réponse s'affiche sous la question. La capture ci-dessous montre une réponse réelle du jeu de démonstration (assistant « Démo Vélanor », conversation « Contrat Batterix », créée le 9 novembre) : la présentation est la même pour tout assistant.

![Réponse citée](img/02-prise-en-main/21-reponse-citee.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | question | question posée, à droite |
| 2 | renvoi « [1] » | numéro du passage qui justifie la phrase ; le survol affiche l'extrait (étape 3) |
| 3 | « 1895 tokens (1841 input, 54 output) · 2.3s » | jetons consommés (consignes et passages en entrée, réponse en sortie) et durée |
| 4 | vignette du document | document cité (`contrat-batterix-scan.pdf`) |

Réponse obtenue : « Le prix unitaire des batteries est de 212 euros HT, ce prix étant révisable une fois par an [1]. De plus, le Fournisseur s'engage à livrer sous 21 jours après la commande [1]. » en 2,3 s. [Vérifié] (`outils/resultats/ragflow/demo-2026-11-09.log`, `outils/resultats/ragflow/captures/02-prise-en-main/21-reponse-citee.txt`)

3. Survoler un renvoi pour lire le passage cité, avec l'image de la page d'origine et le nom du document.

![Extrait cité au survol](img/02-prise-en-main/22-citation.png)

| N° | Élément | Rôle |
|---|---|---|
| 1 | bulle de citation | texte du passage cité, vignette de la page et nom du fichier ; permet de vérifier la réponse |

### Pour aller plus loin

- La question coûte 1 841 jetons d'entrée pour 54 de sortie : l'essentiel est fait des consignes et des passages retrouvés. C'est ce budget qui doit tenir dans le contexte déclaré ; voir [Qualité et performances](12-qualite-et-performances.md).
- Le passage cité vient d'un PDF scanné : l'OCR colle des mots (« Volumeminimalannuel:40 0oo batteries »), sans empêcher la bonne réponse. [Vérifié] (`outils/resultats/ragflow/captures/02-prise-en-main/22-citation.txt`) Voir le manuel [04](04-deepdoc.md).
- Pour une question sans réponse dans les documents, l'assistant répond « The answer you are looking for is not found in the dataset! » (texte réglable, manuel [05](05-assistants-et-citations.md)).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Interface en anglais après connexion | langue mémorisée par le navigateur, anglais par défaut | menu de l'en-tête, « Français » |
| « email and password do not match » alors que le compte existe | compte créé par l'API avec un mot de passe en clair | voir [installation](01-installation.md), section 4 |
| Assistant impossible à relier à la base | analyse pas terminée | attendre que « Nombre de segments » soit rempli |
| La barre du haut disparaît après l'ouverture d'un fichier | la page des passages s'ouvre en plein écran | bouton « Retour » |
| Réponse « The answer you are looking for is not found in the dataset! » | aucun passage assez proche de la question | reformuler, vérifier la base reliée, voir [05](05-assistants-et-citations.md) |

## Sources

- Scénario : `outils/ragflow/captures/captures.py` (scénario `prise_en_main`, phases `base`, `assistant`, `saisie`, `demo`), lancé par `outils/communs/captures/lancer.sh` ; nettoyage : `outils/ragflow/nettoyer_manuel.py`
- Images : `docs/ragflow/img/02-prise-en-main/` ; textes des pages et déroulé : `outils/resultats/ragflow/captures/02-prise-en-main/`
- Jeu de démonstration : `outils/ragflow/demo.py`, [journal](../../outils/resultats/ragflow/demo-2026-11-09.log)
- Documentation officielle : https://ragflow.io/docs/
