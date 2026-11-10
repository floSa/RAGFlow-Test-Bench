# 04. DeepDoc et correction des passages

> **Objet** : savoir ce que DeepDoc lit dans un scan et dans un tableau, ce que cela coûte sur CPU, et corriger à la main un passage mal lu.
> **Prérequis** : [prise en main](02-prise-en-main.md), [datasets et découpage](03-datasets-et-decoupage.md).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré le 9 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : essais dans une base dédiée « Essai-passages », supprimée à la fin ; la base de démonstration n'est pas modifiée.

## Sommaire

1. [Ce que fait DeepDoc](#1-ce-que-fait-deepdoc)
2. [Le scan du corpus](#2-le-scan-du-corpus)
3. [Les tableaux](#3-les-tableaux)
4. [Corriger, désactiver, ajouter un passage](#4-corriger-désactiver-ajouter-un-passage)
5. [Images et modèle de vision](#5-images-et-modèle-de-vision)
6. [Dépannage](#dépannage)
7. [Sources](#sources)

## 1. Ce que fait DeepDoc

### Essentiel

DeepDoc est l'analyseur de documents de RAGFlow : OCR des pages image, reconnaissance de la mise en page (titres, paragraphes, colonnes), structure des tableaux. Ses modèles (format ONNX) sont dans l'image et tournent sur CPU, dans le conteneur `rag-ragflow-server` ; aucun téléchargement n'a lieu au premier usage. [Source] (`Dockerfile`, lignes 25 à 50) Il est choisi dans « Configuration », « Analyseur PDF » : « DeepDOC ».

### Pour aller plus loin

Pendant l'analyse du corpus, la RAM du serveur monte de 0,6 à 2,0 Gio : c'est surtout DeepDoc. [Vérifié] (`outils/resultats/ragflow/banc-2026-11-09-defaut.json`, `pic_ram_mo`) Pour les images, « Parsing method » propose aussi un modèle d'OCR externe (PaddleOCR) ; aucun n'est déclaré ici. [Vérifié] (page « Configuration », manuel [03](03-datasets-et-decoupage.md))

## 2. Le scan du corpus

### Essentiel

`contrat-batterix-scan.pdf` : 2 pages rendues en image, légère rotation et bruit.

| Mesure | Valeur |
|---|---|
| Durée d'analyse (seul dans sa base) | 9,3 s, soit 4,7 s par page |
| Passages produits | 1 (258 jetons) |
| Questions du banc sur ce scan (Q15 à Q18) | 4 bonnes réponses sur 4, bonne page citée |

[Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-passages.log`, `outils/resultats/ragflow/banc-2026-11-09-defaut.json`)

![Passage OCR du contrat](img/02-prise-en-main/06-passages.png)

### Pour aller plus loin

L'OCR est exploitable mais imparfait : espaces perdus (« CONTRATD'APPROVISIONNEMENTN° », « debatteries48V »), « l » lu à la place de « 1 » (« Articlel »), « o » à la place de « 0 » (« 40 0oo batteries », « 1 0o0 cycles »). Le modèle de réponse rétablit le sens : « 40 000 unités » est bien répondu. Une recherche qui dépend du nombre exact est en revanche pénalisée (section 4). [Vérifié] (même journal)

Pour comparaison, Open Notebook 1.15.1 ne lisait pas ce scan (0 question sur 4) : voir le [comparatif](../README.md).

## 3. Les tableaux

### Essentiel

Les tableaux du rapport annuel sont restitués sous forme de tableau (lignes et colonnes) dans le passage, avec leur titre. Le test de récupération montre par exemple le tableau « 5. Effectifs par site » (Nantes 268, Cholet 97, Lyon 31, Bruxelles 16, total 412). Les dix questions de type tableau du banc obtiennent la bonne réponse. [Vérifié] (`outils/resultats/ragflow/banc-2026-11-09-defaut.json` ; texte de la page relevé par `captures.py`, scénario `decoupage`)

### Pour aller plus loin

L'affichage du test de récupération laisse voir des restes de balises autour des titres de tableaux (« ption>7. Fournisseurs principaux ») : le passage contient du HTML, mal rendu à l'écran. Sans effet observé sur les réponses. [Vérifié] (même source)

## 4. Corriger, désactiver, ajouter un passage

### Essentiel

Dans l'interface, cliquer sur un document ouvre ses passages ; chaque passage se modifie, s'active ou se désactive. Par l'API [Testée] :

| Action | Appel |
|---|---|
| Lister | `GET /api/v1/datasets/{base}/documents/{doc}/chunks` |
| Corriger le texte | `PATCH …/chunks/{passage}` avec `{"content": "…"}` |
| Désactiver, réactiver | `PATCH …/chunks` avec `{"chunk_ids": […], "available_int": 0}` (ou 1) |
| Ajouter un passage manuel | `POST …/chunks` avec `{"content": "…", "important_keywords": […]}` |

Effet mesuré sur la recherche « volume minimal annuel de 40 000 batteries » [Vérifié] :

| État du passage | Similarité du passage du contrat |
|---|---|
| texte OCR d'origine (« Volumeminimalannuel:40 0oo ») | 0,346 |
| texte corrigé (« Volume minimal annuel : 40 000 ») | 0,607 |
| passage désactivé | absent des résultats |

(`outils/resultats/ragflow/essai-2026-11-09-passages.log`, script `outils/ragflow/essai_passages.py`)

### Pour aller plus loin

La correction est relue immédiatement par l'API et prise en compte par la recherche sans réanalyse. Un passage ajouté à la main s'ajoute au document (2 passages ensuite). Une nouvelle analyse du document écrase les corrections manuelles [À tester].

## 5. Images et modèle de vision

### Essentiel

Le gabarit Picture et l'option « Enable vision enhancement » demandent un modèle de type `image2text` (« Modèle Img2txt »). Aucun n'est déclaré dans ce banc : [À tester].

### Pour aller plus loin

Le modèle de réponse du socle, Gemma 4 E4B, accepte des images dans vLLM (jusqu'à 4 par requête selon son lancement), et RAGFlow envoie les images au fournisseur VLLM sous forme de blocs `image_url`. Le déclarer aussi en type `image2text` serait donc possible sans nouveau modèle. [Source] (journal de `vllm-central` ; `internal/entity/models/vllm.go`)

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Chiffres faux dans un passage issu d'un scan (« 0oo ») | confusions de l'OCR | corriger le passage (`PATCH …/chunks/{passage}`) |
| Une recherche exacte ne remonte pas le bon passage | mots collés par l'OCR | corriger le passage ou ajouter un passage manuel avec mots-clés |
| Analyse d'un gros PDF scanné très longue | OCR sur CPU, environ 4,7 s par page mesuré | prévoir le temps ; une seule analyse à la fois |

## Sources

- Script et journal : `outils/ragflow/essai_passages.py`, [essai des passages](../../outils/resultats/ragflow/essai-2026-11-09-passages.log)
- Banc : [banc par défaut](../../outils/resultats/ragflow/banc-2026-11-09-defaut.md)
- Code au tag v1.0.0 : `Dockerfile`, `internal/handler/chunk.go` ; documentation : https://ragflow.io/docs/
