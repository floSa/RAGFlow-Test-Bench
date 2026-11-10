# 11. Recettes

> **Objet** : deux cas d'usage complets, de bout en bout : un assistant documentaire d'entreprise et une ingestion automatique quotidienne.
> **Prérequis** : [prise en main](02-prise-en-main.md), [assistants de chat et citations](05-assistants-et-citations.md), [API HTTP et SDK Python](10-api-et-sdk.md).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), `ragflow-sdk` 1.0.0, Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré le 9 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : documents fictifs ; la recette 2 travaille dans une base et un dossier d'essai supprimés à la fin.

## Sommaire

1. [Assistant documentaire d'entreprise](#1-assistant-documentaire-dentreprise)
2. [Ingestion automatique quotidienne](#2-ingestion-automatique-quotidienne)
3. [Dépannage](#dépannage)
4. [Sources](#sources)

## 1. Assistant documentaire d'entreprise

### Essentiel

But : répondre aux questions des salariés sur les documents de l'entreprise, avec la source de chaque réponse. Recette appliquée par `outils/ragflow/demo.py` [Testée] :

1. Base « Démo Vélanor », gabarit General, les 9 documents du corpus (PDF, scan, DOCX, PPTX, XLSX, HTML, Markdown, audio, anglais) : 26 passages en 52 à 61 s.
2. Assistant relié à la base, réglé d'après le banc : `top_n` 8, poids des vecteurs 0,7.
3. Message d'accueil et message de réponse vide en français.
4. Une conversation par sujet.

| Conversation | Durée | Réponse obtenue |
|---|---|---|
| Contrat Batterix | 2,3 s | « Le prix unitaire des batteries est de 212 euros HT, ce prix étant révisable une fois par an [ID:0]. De plus, le Fournisseur s'engage à livrer sous 21 jours après la commande [ID:0]. » |
| Objectifs 2026 | 2,0 s | « Vélanor vise un chiffre d'affaires de 55 M€ en 2026 [ID:0][ID:3]. … ce qui prévoit 70 embauches [ID:0]. » |
| Audit fournisseur (en anglais) | 1,4 s | « Batterix received an overall score of 87 out of 100 during the Supplier Quality Audit [ID:0]. The measured cell defect rate was 0.3% [ID:0]. » |

[Vérifié] (`outils/resultats/ragflow/demo-2026-11-09.log`)

### Pour aller plus loin

L'assistant répond dans la langue de la question (anglais pour la troisième). Il reste ouvert dans l'interface (« Discussion », « Démo Vélanor ») avec ses trois conversations. Pour des documents scannés, ajouter la correction des passages mal lus (manuel [04](04-deepdoc.md)).

## 2. Ingestion automatique quotidienne

### Essentiel

But : verser chaque jour dans une base les nouveaux fichiers d'un dossier partagé, sans doublon. Script `outils/ragflow/recette_ingestion.py` [Testée] :

```bash
uv run python outils/ragflow/recette_ingestion.py /chemin/du/dossier "Nom de la base"
```

Il crée la base si besoin, compare les noms de fichiers à ceux déjà présents, téléverse les nouveaux, lance l'analyse et attend la fin. Essai sur trois « jours » :

| Jour | Fichiers déposés | Ajoutés | Documents dans la base |
|---|---|---|---|
| 1 | `cse-2025-10-14.md`, `faq-sav.html` | 2 (en 3 s) | 2 |
| 2 | aucun | 0 | 2 |
| 3 | `procedure-batteries.docx` | 1 (en 3 s) | 3 |

Question posée ensuite : « Les batteries doivent être stockées entre 10 °C et 25 °C, dans le local B2 qui est équipé d'une détection incendie [ID:0]. » (1,7 s). [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-recette-ingestion.log`)

### Pour aller plus loin

Lancement quotidien par `cron` dans WSL, par exemple à 7 h [Aide] :

```text
0 7 * * * cd ~/mes_projets/Tutoriels/RAGFlow-Test-Bench && ~/.local/bin/uv run python outils/ragflow/recette_ingestion.py /chemin/du/dossier "Nom de la base" >> donnees/ingestion.log 2>&1
```

Un fichier modifié sous le même nom n'est pas réimporté : la comparaison se fait par nom. Pour suivre les modifications, il faudrait comparer une empreinte et supprimer l'ancien document avant de réimporter [À tester]. Pour un site web, la synchronisation par sitemap fait ce travail (manuel [09](09-sources-externes.md)).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Un fichier modifié n'est pas repris | comparaison par nom | renommer, ou supprimer l'ancien document |
| Assistant impossible à créer juste après l'import | analyse pas terminée | le script attend `chunk_count` > 0 avant de rendre la main |

## Sources

- Scripts : `outils/ragflow/demo.py`, `outils/ragflow/recette_ingestion.py`, `outils/ragflow/client.py`
- Journaux : [démonstration](../../outils/resultats/ragflow/demo-2026-11-09.log), [ingestion](../../outils/resultats/ragflow/essai-2026-11-09-recette-ingestion.log)
