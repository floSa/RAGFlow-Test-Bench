# A6. Rapport d'essais

> **Objet** : dire comment chaque affirmation du manuel a été établie (corpus, banc, captures, relectures), ce que signifient les étiquettes, où se trouve la preuve de chaque chapitre de la partie 1, quels défauts de RAGFlow ont été rencontrés et ce qui n'a pas été vérifié.
> **Prérequis** : aucun pour la lecture ; pour rejouer un essai, RAGFlow installé (chapitre [02](../manuel/02-installer-ragflow.md)) et le dépôt cloné.
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré les 9 et 11 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : les essais ont été faits sur des données fictives, dans des objets nommés « Manuel-… » ou « Banc-… » supprimés ensuite (`outils/ragflow/nettoyer_manuel.py`, `outils/ragflow/nettoyer_essais.py`) ; le jeu de démonstration « Démo Vélanor » n'est que lu. Les jetons d'accès sont masqués sur les captures et remplacés par `<masqué>` dans les textes archivés. Le bilan de mission est dans le [rapport RAGFlow](../../../RAPPORT-ragflow.md).

## Sommaire

1. [Méthode](#1-méthode)
2. [Signification des étiquettes](#2-signification-des-étiquettes)
3. [Tableau des preuves par chapitre](#3-tableau-des-preuves-par-chapitre)
4. [Affirmations vérifiées, chapitre par chapitre](#4-affirmations-vérifiées-chapitre-par-chapitre)
5. [Essais par l'API qui complètent les chapitres](#5-essais-par-lapi-qui-complètent-les-chapitres)
6. [Défauts de RAGFlow rencontrés](#6-défauts-de-ragflow-rencontrés)
7. [Incidents des essais](#7-incidents-des-essais)
8. [Ce qui n'a pas été vérifié](#8-ce-qui-na-pas-été-vérifié)
9. [Dépannage](#dépannage)
10. [Sources](#sources)

## 1. Méthode

### 1.1 Corpus et questions de référence

- **Corpus fictif** : neuf documents d'une entreprise fictive, Vélanor (fabricant de vélos électriques), générés par `outils/communs/generer_corpus.py` à graine fixe, empreintes SHA-256 dans `corpus/MANIFEST.json` : rapport annuel PDF texte avec tableaux (`rapport-annuel-2025.pdf`), contrat scanné (`contrat-batterix-scan.pdf`, pages rendues en image, légère rotation, bruit), procédure DOCX, présentation PPTX, classeur XLSX, page HTML (FAQ du service après-vente), note Markdown (compte rendu du CSE), audit en anglais (`supplier-audit-batterix-en.pdf`) et message vocal MP3 (synthèse vocale locale, `outils/communs/generer_audio.py`). Le corpus est partagé par toutes les solutions de la série. [Vérifié] (`corpus/documents/`, `corpus/MANIFEST.json`)
- **Questions de référence** : 38 questions dans `corpus/questions.json`, avec réponse attendue, document et page sources, et type : 13 faits simples, 10 tableaux, 4 sur le PDF scanné, 3 multi-documents, 2 en anglais, 2 sur l'audio, et 4 pièges sans réponse dans le corpus. [Vérifié] (`corpus/questions.json`)

### 1.2 Banc

- Interface commune dans `outils/communs/banc/` (`commun.py`, tableau comparatif `tableau.py`, renotation `renoter.py`) ; adaptateur RAGFlow `outils/ragflow/banc.py`, variantes enchaînées par `outils/ragflow/serie_banc.sh`.
- Une session neuve par question, posée par `POST /api/v1/chat/completions`. Exactitude : la réponse contient les valeurs attendues ; pour un piège, elle signale l'absence d'information. Citation : le bon document figure parmi les passages marqués `[ID:n]` dans la réponse ; page vérifiée quand RAGFlow l'expose. Pas de juge LLM.
- Mesures : latence p50 et p95, temps d'indexation, RAM de l'application seule (`docker stats`, hors conteneurs de modèles), VRAM (`nvidia-smi`).
- Sorties : `outils/resultats/ragflow/banc-2026-11-09-*.json` et `.md`. Résultats, variantes et préconisations : annexe [A1](A1-evaluation-qualite-et-performances.md) ; profils matériels : annexe [A2](A2-choisir-son-materiel-et-ses-modeles.md).

### 1.3 Captures annotées

- Playwright exécuté dans le conteneur officiel `mcr.microsoft.com/playwright/python:v1.64.1-noble`, figé par empreinte dans `outils/communs/captures/lancer.sh`, branché sur le réseau `rag-local` ; rien installé dans WSL.
- Chaque geste est fait à la souris, comme un utilisateur. `outils/communs/captures/annoter.py` dessine, juste avant la capture, un rectangle rouge et une pastille numérotée autour de chaque élément cité ; le tableau N° | Élément | Rôle qui suit l'image a autant de lignes que de pastilles.
- Scénarios : `outils/ragflow/captures/captures.py` (visite, installation, prise en main, diagnostic de connexion), `carte.py` (carte de l'interface), `manuels_03_06.py`, `manuels_07_15.py`, `manuels_10_14.py` ; préparation côté WSL pour le dernier lot : `outils/ragflow/manuels_10_14_preparer.py`.
- Traçabilité : pour chaque capture, le texte de la page et la liste de ses éléments visibles sont enregistrés sous le même nom dans `outils/resultats/ragflow/captures/<dossier>/` ; le déroulé, les durées et les requêtes observées sont dans le `scenario.log` du dossier ; le nettoyage des objets d'essai dans `nettoyage.log`.
- Règle : une capture par action ou par écran nouveau ; une étape qui revient sur un écran déjà montré y renvoie. 164 captures annotées au total, plus 35 captures de repérage de la carte (`docs/ragflow/img/carte/`).

### 1.4 Relectures et vérification

- **Relecture adversariale** (9 novembre 2026) par un sous-agent neuf, qui n'avait pas écrit les manuels : environ 95 affirmations confirmées, 21 écarts, traités par archivage de preuves complémentaires (`outils/resultats/ragflow/preuves-2026-11-09/`), corrections de valeurs et requalifications. [Vérifié] (`JOURNAL.md`, entrée « Phase H : clôture »)
- **Vérificateur** `outils/communs/verifier_docs.py` lancé avant chaque commit : liens et images relatifs, ancres, ton impersonnel, absence de pictogrammes, gabarit de la partie 1 (« Point de départ », mention « Où », légende « Écran : », tableau après chaque capture, aucune étiquette), en-tête et étiquettes des annexes, aucune image inutilisée, carte de l'interface complète. Résultat archivé du 9 novembre : `outils/resultats/ragflow/verifier-docs-2026-11-09.txt`.
- **Relecture par un lecteur novice** de la partie 1 restructurée : prévue par la mission (`kit/PROMPT.md`, phase H), à consigner dans `JOURNAL.md`.

### 1.5 Machine et socle

- Machine de profil B : Ryzen 5 9600X, 32 Go de RAM dans WSL2, RTX 4060 Ti 16 Go, Ubuntu 24.04.5, Docker 29.9.3. Diagnostic : `outils/resultats/machine/diagnostic-2026-11-09.json`.
- Modèles servis par LLM-Service (branche `service-vllm`), partagé avec d'autres applications et jamais modifié depuis ce dépôt ; voix par `rag-speaches` (`outils/communs/voix.sh`). Le 11 novembre, `vllm-central` a dû être remis en service avant les captures de la question réelle : `outils/resultats/ragflow/preuves-2026-11-11/llm-service-reparation.log`.

## 2. Signification des étiquettes

La partie 1 n'affiche aucune étiquette : ses affirmations sont reprises ici avec la leur.

| Étiquette | Sens | Preuve exigée |
|---|---|---|
| [Vérifié] | observé ou mesuré sur la machine d'essai, les 9 ou 11 novembre 2026 | un résultat brut dans `outils/resultats/` (journal, JSON, texte de capture) ou une capture |
| [Source] | lu dans la documentation officielle ou le code source au tag v1.0.0, non rejoué | le fichier du dépôt officiel cité |
| [Estimation] | calcul ou déduction, non mesuré | le calcul et les mesures dont il part |
| [À tester] | non documenté et non essayé | la raison de l'absence d'essai |
| [Testée] | commande exécutée telle quelle | le journal de l'essai ou le script qui la contient |

## 3. Tableau des preuves par chapitre

Chemins relatifs à la racine du dépôt. « Captures » : dossier de textes et de déroulé dans `outils/resultats/ragflow/captures/`.

| Chapitre | Scénario de captures | Captures (résultats bruts) | Scripts et journaux d'essai |
|---|---|---|---|
| [01. Découvrir RAGFlow](../manuel/01-decouvrir-ragflow.md) | aucun (pas de capture) | aucun | `outils/communs/identite_github.py`, `outils/resultats/ragflow/identite-github-2026-11-09.json` ; résultats du banc : annexe [A1](A1-evaluation-qualite-et-performances.md) |
| [02. Installer RAGFlow](../manuel/02-installer-ragflow.md) | `captures.py`, scénario `installation` ; `relecture_novice.py`, scénario `inscription` (capture refaite) | `01-installation/`, `relecture/inscription.log` | `outils/ragflow/installer.sh`, `configurer.py`, `verif_minimale.py`, `essai_reinstallation.sh`, `ressources.sh` ; `installation-2026-11-09*.log`, `ports-2026-11-09.txt`, `essai-2026-11-09-reinstallation.log` ; détail : annexe [A4](A4-exploitation.md) |
| [03. Premiers pas](../manuel/03-premiers-pas.md) | `captures.py`, scénarios `visite`, `installation`, `prise_en_main` (phase `base`), `diag_connexion` ; `relecture_novice.py`, scénario `modeles` (modèles listés, enregistrement des modèles par défaut, libellés de connexion en français) ; `manuels_10_14.py`, scénario `qualite` (fenêtre « Modifier le modèle ») | `00-notions-fondamentales/`, `01-installation/`, `02-prise-en-main/`, `12-qualite-et-performances/02-tokens-maximum.txt`, `relecture/modeles.log` | `outils/ragflow/configurer.py`, `configuration-2026-11-09.log` |
| [04. Première question en dix minutes](../manuel/04-premiere-question.md) | `captures.py`, scénario `prise_en_main` (phases `base`, `assistant`, `envoi`) | `02-prise-en-main/` | `outils/ragflow/demo.py`, `demo-2026-11-09.log`, `installation-2026-11-09-verif-essai1.log` |
| [05. Ajouter et organiser ses documents](../manuel/05-ajouter-et-organiser-ses-documents.md) | `manuels_03_06.py`, scénario `decoupage` (phases `base`, `fichiers`, `groupe`, `journaux`, `gestion`) | `03-datasets-et-decoupage/` | `carte/05-base-fichiers.txt`, `carte/27-gestion-des-fichiers.txt` |
| [06. Régler la lecture des documents](../manuel/06-regler-la-lecture-des-documents.md) | `manuels_03_06.py`, scénarios `decoupage` (phases `gabarit`, `config`, `pipelines`) et `deepdoc` | `03-datasets-et-decoupage/`, `04-deepdoc/` | `outils/ragflow/essai_passages.py`, `essai-2026-11-09-passages.log` ; bancs par gabarit : annexe [A1](A1-evaluation-qualite-et-performances.md) ; DeepDoc : annexe [A5](A5-fonctionnement-interne.md) |
| [07. Poser des questions et lire les sources](../manuel/07-poser-des-questions-et-lire-les-sources.md) | `manuels_03_06.py`, scénarios `assistants` (phases `conversation`, `ecran`) et `agentique` | `05-assistants-et-citations/`, `06-agentic-rag/` | `outils/ragflow/banc.py` (`--agentic`), `banc-2026-11-09-agentic.json` |
| [08. Régler un assistant](../manuel/08-regler-un-assistant.md) | `manuels_03_06.py`, scénario `assistants` (phases `creation`, `parametres`, `test`) | `05-assistants-et-citations/` | `banc-2026-11-09-defaut.json`, `banc-2026-11-09-hybride-vecteurs07-top8.json`, `essai-2026-11-09-sdk-defauts.log` |
| [09. Rechercher dans ses documents](../manuel/09-rechercher.md) | `manuels_07_15.py`, scénario `recherche` (phases `creation`, `reglages`, `question`) | `15-recherche/` | `outils/ragflow/nettoyer_manuel.py`, `captures/15-recherche/nettoyage.log` |
| [10. Construire un agent](../manuel/10-agents.md) | `manuels_07_15.py`, scénario `agents` (fenêtre « Publier » reprise du scénario `compilation`) (phases `liste`, `modele`, `canevas`, `essai`, `conversation`, `gestion`, `json`, `blanc`, `memoire`, `memoire_page`, `memoire_agent`, `mcp`) ; `relecture_novice.py`, scénario `export` (menu « Gestion », fichier téléchargé) | `08-agents/`, `relecture/export.log` | `outils/ragflow/essai_agent.py`, `essai-2026-11-09-agent.log` (section 5) |
| [11. Produire des synthèses automatiques](../manuel/11-syntheses-automatiques.md) | `manuels_07_15.py`, scénario `compilation` (phases `operateur`, `pipeline`, `base`, `configuration`, `import`, `artefacts`, `autres`, `echec`, `vues`) | `07-knowledge-compilation/` (dont `echec-wiki.log`, `echec-pageindex.log`, `incident-pipeline-demo.txt`) | `outils/ragflow/essai_compilation.py`, `essai-2026-11-09-compilation-*.log`, `preuves-2026-11-09/compilation-builtins.json` (section 5) |
| [12. Alimenter une base depuis une source externe](../manuel/12-sources-externes.md) | `manuels_07_15.py`, scénario `sources` (phases `ajout`, `detail`, `liaison`, `journaux`, `canaux`) | `09-sources-externes/` | `outils/ragflow/essai_sitemap.py`, `essai_sitemap_autorise.sh`, site `outils/ragflow/site-test/` ; `essai-2026-11-09-sitemap-refus.log`, `essai-2026-11-09-sitemap-autorise.log` (section 5) |
| [13. Gérer son compte, son équipe et ses clés](../manuel/13-comptes-equipe-et-cles.md) | `manuels_10_14.py`, scénarios `exploitation` (phases `equipe`, `profil`, `admin`) et `cles` ; `relecture_novice.py`, scénario `invitation` (compte invité inscrit, invitation acceptée, base passée en « Équipe » et vue par l'invité, compte supprimé ensuite) | `13-exploitation/`, `10-api-et-sdk/`, `relecture/invitation.log`, `relecture/nettoyage.log` | `outils/ragflow/essai_admin.py`, `essai-2026-11-09-admin.log` ; API et SDK : annexe [A3](A3-automatiser-par-l-api.md) |
| [14. Cas pratiques](../manuel/14-cas-pratiques.md) | `manuels_10_14.py`, scénario `recettes` | `11-recettes/` (dont `ingestion.log`) | `outils/ragflow/demo.py`, `recette_ingestion.py`, `manuels_10_14_preparer.py`, `client.py` ; `demo-2026-11-09.log`, `essai-2026-11-09-recette-ingestion.log` |
| [15. En cas de problème](../manuel/15-en-cas-de-probleme.md) | `manuels_10_14.py`, scénario `depannage` ; fenêtre « Modifier le modèle » montrée au chapitre 03 ; assistant d'essai par `manuels_10_14_preparer.py assistant` | `14-depannage/` (dont `contexte.log`, `preparation.log`) | `outils/ragflow/contexte.py`, `essai_contexte.py` ; journaux cités au tableau du chapitre (section 4) |
| [16. Glossaire](../manuel/16-glossaire.md) | aucun | aucun | définitions reprises du [glossaire de la série](../../glossaire.md) |
| [Carte de l'interface](carte-interface.md) | `carte.py` | `carte/` (35 captures de repérage) | — |

## 4. Affirmations vérifiées, chapitre par chapitre

Les chiffres de la partie 1, avec leur étiquette et leur preuve. Sauf mention, les fichiers sont dans `outils/resultats/ragflow/`.

### 4.1 Chapitre 01. Découvrir RAGFlow

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Licence Apache-2.0 ; 93 880 étoiles, 11 278 forks ; 2 763 modifications sur 90 jours, 925 contributeurs ; projet créé en décembre 2023 ; v1.0.0 publiée le 6 novembre 2026 | [Vérifié] | `identite-github-2026-11-09.json` (relevé du 9 novembre), `versions-2026-11-09.json` |
| Réécriture en Go de l'ancien serveur Python | [Source] | `docs/release_notes.md` au tag v1.0.0 |
| Résultats mesurés en cinq lignes (33 sur 34, 34 sur 34 avec réglages, 1,28 s en médiane, scan lu 4 sur 4) | [Vérifié] | annexe [A1](A1-evaluation-qualite-et-performances.md) ; `banc-2026-11-09-defaut.md` |
| Configurations minimales sans et avec carte graphique | [Vérifié] avec GPU, [Estimation] sans GPU | annexe [A2](A2-choisir-son-materiel-et-ses-modeles.md) |

### 4.2 Chapitre 02. Installer RAGFlow

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Compose officiel : ports sur `0.0.0.0` et mots de passe connus (`infini_rag_flow`, `admin`) | [Source] | `docker/docker-compose.yml`, `docker/docker-compose-base.yml`, `docker/.env` ; `relecture.md` |
| Téléchargement des six images en 57 s, premier démarrage sain en 39 s | [Vérifié] | `installation-2026-11-09-pull.log`, `installation-2026-11-09.log` |
| Port 8080 déjà occupé, interface publiée sur 8088 | [Vérifié] | `preuves-2026-11-09/port-8080.txt` |
| Ports publiés sur `127.0.0.1` seulement | [Vérifié] | `ports-2026-11-09.txt` |
| `vm.max_map_count` à 262 144, Docker dans Ubuntu (`/var/lib/docker`) | [Vérifié] | `outils/resultats/machine/diagnostic-2026-11-09.json` |
| Aucun modèle téléchargé à l'installation ; modèles DeepDoc dans l'image | [Source] et [Vérifié] | `Dockerfile` (lignes 25 à 50) ; `preuves-2026-11-09/acces-sortants.txt` |
| Vérification minimale : réponse citée en 4,0 s par l'API HTTP, quatre passages de `cse-2025-10-14.md` | [Vérifié] | `installation-2026-11-09-verif.log` |
| Cycle désinstallation, réinstallation, configuration, vérification : 14 s, 39 s, moins d'une seconde, 7 s ; aucun conteneur ni volume restant | [Vérifié] | `essai-2026-11-09-reinstallation.log` |
| Mémoire par service, disque, override : détail | [Vérifié] | annexe [A4](A4-exploitation.md) ; `ressources-2026-11-09-*.txt`, `preuves-2026-11-09/mysql-disque.txt` |
| Mise à jour : aucune version plus récente que v1.0.0 le jour des essais | [À tester] | `versions-2026-11-09.json` ; `docs/release_notes.md` |

### 4.3 Chapitre 03. Premiers pas

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Langue mémorisée par le navigateur (clé `lng`), pas par le compte ; changer la langue du compte par l'API ne traduit pas l'interface | [Vérifié] | `web/src/locales/config.ts` ; essais des captures, `captures/02-prise-en-main/` |
| Liens de l'en-tête (Discord, GitHub, guide officiel) | [Vérifié] | `web/src/layouts/components/header.tsx` ; `captures/00-notions-fondamentales/` |
| Trois pages en plein écran (« Artifacts », passages, canevas) | [Vérifié] | `captures/carte/` |
| Instance « Manuel-instance » créée puis supprimée à la souris ; modèles déclarés (`gemma4:e4b`, `bge-m3`, `Systran/faster-whisper-small`) | [Vérifié] | `captures/01-installation/` ; `configuration-2026-11-09.log` |
| Compte `admin@ragflow.io` réservé à l'administration, refusé sur l'API ordinaire | [Source] | `internal/handler/auth.go` |
| Mot de passe envoyé par l'interface sous la forme `RSA(base64(mot de passe))` : un compte créé par l'API en clair est refusé dans le navigateur | [Vérifié] | `internal/common/password.go` ; `captures.py`, scénario `diag_connexion` |
| RAGFlow ne fixe pas `num_ctx` : réponse bornée à « contexte déclaré − jetons du prompt » ; une question consomme 600 à 3 300 jetons | [Source] et [Vérifié] | `internal/service/chat_pipeline.go` ; `captures/02-prise-en-main/21-reponse-citee.txt`, `preuves-2026-11-09/textes-captures/02-conversation.txt` |
| Chemin Ollama sans carte graphique | [À tester] | non essayé (machine avec GPU) |

### 4.4 Chapitre 04. Première question en dix minutes

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Deux fichiers analysés en moins de 7 s : 4 passages pour le compte rendu, 1 pour la FAQ | [Vérifié] | `captures/02-prise-en-main/scenario.log` |
| Neuf documents (1 Mo) : 26 passages en 52 à 56 s, OCR du scan compris | [Vérifié] | `demo-2026-11-09.log`, `banc-2026-11-09-defaut.json` |
| Gabarit choisi d'office : « Presentation » pour le diaporama, « Audio » pour le son | [Vérifié] | `captures/carte/05-base-fichiers.txt` |
| Un assistant ne peut pas être relié à une base sans passage (« doesn't own parsed file ») | [Vérifié] | `installation-2026-11-09-verif-essai1.log` |
| Relance d'analyse précédée d'une confirmation qui annonce la suppression des passages | [Source] | `web/src/locales/fr.ts`, clé `redo` |
| Message « Modifié » à l'enregistrement de l'assistant | [Vérifié] | `captures/02-prise-en-main/scenario.log` |
| Réponse « 1 150 euros par salarié, versée en avril 2026 [1] », conforme à Q27, 3,4 s après le clic, 1,3 s de génération ; 611 jetons d'entrée et 41 de sortie | [Vérifié] | `captures/02-prise-en-main/scenario.log`, `21-reponse-citee.txt` ; `corpus/questions.json` |
| Une question sur le contrat Batterix coûte 1 841 jetons d'entrée sur la base de démonstration | [Vérifié] | `demo-2026-11-09.log`, `preuves-2026-11-09/textes-captures/02-conversation.txt` |
| Vignette de la page citée pour un PDF, pas pour un Markdown | [Vérifié] | `captures/carte/15-discussion-conversation.txt` |
| Réglages par défaut d'un assistant : 6 passages, mots-clés 0,7, vecteurs 0,3 | [Vérifié] | `banc-2026-11-09-defaut.json` |

### 4.5 Chapitre 05. Ajouter et organiser ses documents

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Trois fichiers analysés en moins de 6 s | [Vérifié] | `captures/03-datasets-et-decoupage/scenario.log` |
| Téléversement local : 32 fichiers et 1 Go au plus par envoi | [Vérifié] | `captures/03-datasets-et-decoupage/05-televersement-analyse.txt` |
| Relance d'analyse d'un document court : moins de 3 s ; passages existants effacés puis recalculés | [Vérifié] | même `scenario.log` |
| Une relance efface les corrections manuelles | [Source] | `web/src/locales/fr.ts`, clé `redo` |
| Dossier `.knowledgebase` de « Gestion des fichiers » : un sous-dossier par base | [Vérifié] | `captures/carte/27-gestion-des-fichiers.txt` |

### 4.6 Chapitre 06. Régler la lecture des documents

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Tableur : 2 passages avec « General », 10 avec « Table », 3 s après la confirmation | [Vérifié] | `captures/03-datasets-et-decoupage/scenario.log` |
| Modèle d'embedding changeable tant que la base n'a pas de passages, ou si les vecteurs restent proches (similarité moyenne d'au moins 0,9) | [Source] | `web/src/locales/fr.ts`, clé `embeddingModelTip` |
| « Splits at: » et délimiteurs entre accents graves | [Source] | `web/src/locales/en.ts`, clé `delimiterTip` |
| Langue de la base relue « French » et description conservée après rechargement | [Vérifié] | même `scenario.log` |
| Effet de la langue « English » par défaut sur la recherche d'un corpus français | [À tester] | non essayé |
| Liste des gabarits ; anciens gabarits `tag` et `knowledge_graph` retirés ; pipeline personnalisé (`parse_type=2`) | [Source] | `docs/references/http_api_reference.md` |
| Passages et jetons par gabarit, indexation en 53 à 56 s quel que soit le gabarit, effet sur le banc | [Vérifié] | annexe [A1](A1-evaluation-qualite-et-performances.md) ; `banc-2026-11-09-{defaut,gabarit-paper,gabarit-presentation,gabarit-table}.json` |
| Écart de jetons du gabarit Table dû à la répétition des en-têtes | [Estimation] | même source |
| Scan analysé en 10,8 s (10 s de lecture) ; 1 passage pour 2 pages ; erreurs d'OCR | [Vérifié] | `captures/04-deepdoc/scenario.log`, `05-resultat-du-segment.txt` ; annexe [A5](A5-fonctionnement-interne.md) |
| Passage OCR à 34,55 au test de récupération ; passage ajouté à 83,17 | [Vérifié] | `captures/04-deepdoc/scenario.log` |
| « Confirmer » sans effet sur un passage de PDF modifié, enregistré sur un passage Markdown | [Vérifié] | même journal (section 6 de cette annexe) |
| Restes de balises dans les tableaux affichés | [Vérifié] | `captures/05-assistants-et-citations/20-test-resultats.txt` |
| Analyseurs autres que « DeepDOC » ; gabarit Picture et « Enable vision enhancement » | [À tester] | annexe [A5](A5-fonctionnement-interne.md) |

### 4.7 Chapitre 07. Poser des questions et lire les sources

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Q30 réglé (vecteurs 0,7, « Top N » 8) : 21 jours et 24 jours, chacun cité, 3,9 s après le clic | [Vérifié] | `captures/05-assistants-et-citations/22-reponse-citee.txt`, `scenario.log` |
| Refus d'une question hors corpus (Q35) par la phrase du « Prompt système », suivi d'un renvoi ; un renvoi ne prouve pas qu'une réponse a été trouvée | [Vérifié] | `captures/05-assistants-et-citations/26-question-sans-reponse.txt`, `scenario.log` |
| Conversations non renommables (menu « … » limité à « Supprimer ») | [Vérifié] | même journal ; `web/src/pages/next-chats/chat/conversation-dropdown.tsx` |
| Pièce jointe : 5 fichiers au plus, 5 Mo chacun ; conversation nommée d'après le fichier | [Vérifié] | `captures/05-assistants-et-citations/30-piece-jointe.txt` ; carte de l'interface |
| Lecture à voix haute et micro : modèles absents du banc | [À tester] | `web/src/components/ui/audio-button.tsx` [Source] |
| Page intégrée servie à l'adresse du serveur, `127.0.0.1` seulement | [Vérifié] | `ports-2026-11-09.txt` |
| « Agentic » sur Q30 : 5,4 s, 32 205 jetons d'entrée, délai constaté manqué ; premier passage complet (31 988 jetons) ; mode instable | [Vérifié] | `captures/06-agentic-rag/scenario.log`, `03-reponse-agentic.txt` |
| « Naive » par défaut sur Q30 : 24 jours seulement, 5,9 s et 1 524 jetons d'entrée (3,9 s, 1 710 jetons au premier passage) | [Vérifié] | `captures/06-agentic-rag/scenario.log`, `04-reponse-naive.txt` |
| Exploration agentique au-delà des 16 384 jetons déclarés, acceptée par vLLM lancé à 32 768 | [Vérifié] | `preuves-2026-11-09/vllm-extrait.log` |
| Mode agentique sur un serveur limité à 16 384 jetons | [À tester] | non essayé |
| `"reasoning": 5` dans `POST /api/v1/chat/completions` ; gabarit `smart-reasoning` (`conf/agentic_rag.yaml`) | [Testée] et [Source] | `outils/ragflow/banc.py` (`--agentic`) ; `internal/service/chat_pipeline.go` |
| Banc Naive contre Agentic (33 contre 30 sur 34, multi-documents 3 sur 3, échecs Q06, Q07, Q26, Q27 sans recherche, bloc `<think>` 38 fois sur 38) | [Vérifié] | annexe [A1](A1-evaluation-qualite-et-performances.md) ; `banc-2026-11-09-agentic.json` |
| Un modèle plus grand suivrait mieux le déroulé agentique ; « Decision model » | [Estimation] ; [À tester] | non essayé |

### 4.8 Chapitre 08. Régler un assistant

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Réglages de « Paramètres du modèle » tous désactivés à la création | [Vérifié] | `captures/05-assistants-et-citations/07-parametres-du-modele.txt` |
| Valeurs affichées à la création à la souris : seuil 20, mots-clés 0,7, « Rerank candidates » 64, « Top N » 8 | [Vérifié] | `captures/05-assistants-et-citations/scenario.log` |
| Après « Enregistrer » et rechargement : « Top N » 8, mots-clés 0,3, réponse vide et base conservées | [Vérifié] | même journal |
| Test de récupération sur Q30 : 25 passages, premier à 42,50 (25,87 mots-clés, 81,31 vecteurs) ; avec vecteurs 0,7 : 26 passages, premier à 64,68 | [Vérifié] | `captures/05-assistants-et-citations/20-test-resultats.txt`, `21-test-vecteurs-07.txt` |
| Même test par `POST /api/v1/retrieval` | [Testée] | `outils/ragflow/essai_passages.py`, `exemples/ragflow/05_recherche_seule.py` |
| Banc : 33 sur 34 par défaut, 34 sur 34 avec vecteurs 0,7 et `top_n` 8 (+0,08 s en médiane) | [Vérifié] | annexe [A1](A1-evaluation-qualite-et-performances.md) ; `banc-2026-11-09-defaut.json`, `banc-2026-11-09-hybride-vecteurs07-top8.json` |
| Par l'API, seul `vector_similarity_weight` se règle ; lire `keywords_similarity_weight` | [Vérifié] | `essai-2026-11-09-sdk-defauts.log` ; `internal/handler/chat.go` (ligne 339) |
| Aucun reranker embarqué | [Source] | `internal/entity/models/builtin.go` |
| Reranker TEI 1.8.2 (`rag-reranker`, processeur) : sain en 22 s, 4,6 Gio de RAM ; format natif `/rerank` en 200, format envoyé par RAGFlow en 422 « missing field `texts` », `/v1/rerank` en 404 : RAGFlow ne peut pas l'appeler | [Vérifié] | `reranker-2026-11-11.log`, `reranker-cpu-2026-11-11-tei.log` ; annexe [A1](A1-evaluation-qualite-et-performances.md), section 7 |
| Pilotes de rerank de RAGFlow au format Jina/Cohere ; pilote « HuggingFace » sans rerank | [Source] | `internal/entity/models/vllm.go`, `huggingface.go` |
| Reranker vLLM à côté de `vllm-central` et `vllm-embed` : non démarré, VRAM libre de 211 à 461 Mio pour un besoin d'environ 1,6 Go | [Vérifié] ; [Estimation] pour le besoin | `reranker-2026-11-11.log` ; annexe [A2](A2-choisir-son-materiel-et-ses-modeles.md), section 6 |
| Classement avec reranker : mots-clés × poids + note du reranker × poids des vecteurs ; nom `BAAI/bge-reranker-v2-m3` pris pour un ancien reranker intégré | [Source] | `internal/service/nlp/reranker.go`, `internal/service/chat.go` |

### 4.9 Chapitre 09. Rechercher dans ses documents

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Passages en 0,3 à 0,8 s, recherches connexes après 5,6 à 6,1 s, carte mentale 3 s après le clic (trois passages du scénario) | [Vérifié] | `captures/15-recherche/scenario.log` |
| Résumé juste (1 150 euros, avril 2026) ; « Total » 24 passages ; filtre « 0/9 » | [Vérifié] | `captures/15-recherche/06-resultats.txt` |
| Message « Model is required when AI summary, related search, or query mindmap is enabled » | [Vérifié] | `captures/15-recherche/scenario.log` |
| Surlignage qui coupe les mots ; balisage brut des tableaux dans les passages | [Vérifié] | capture `15-recherche/06-resultats.png`, `06-resultats.txt` |
| Remonter le « Seuil de similarité » réduit le bruit | [À tester] | non essayé |
| Jeton `auth=` du code d'intégration masqué ; recherches listées et supprimées par `GET` et `DELETE /api/v1/searches` | [Vérifié] | `captures/15-recherche/nettoyage.log` |
| Langue des consignes des recherches connexes | [À tester] | non essayé |

### 4.10 Chapitre 10. Construire un agent

| Affirmation | Étiquette | Preuve |
|---|---|---|
| 19 gabarits en anglais, dont plusieurs supposent un service en ligne et deux pipelines d'ingestion ; liste aussi par `GET /api/v1/agents/templates` | [Vérifié] ; [Testée] | `essai-2026-11-09-agent.log` ; `captures/08-agents/scenario.log` |
| Panneau du bloc agent : « Paramètres avancés », outils disponibles | [Vérifié] | `captures/08-agents/05-agent.txt`, `scenario.log` |
| « Type de fichier à télécharger » | [À tester] | non essayé |
| Réponses justes, en anglais, en 5,4 s (« Exécuter ») et 6,3 s (« Lancer ») | [Vérifié] | `captures/08-agents/scenario.log` (lignes « réponse dans ») ; `JOURNAL.md` |
| Version publiée « v1 » dans « Historique des versions » ; heure de Paris dans le nom, heure universelle dans « Créé » | [Vérifié] | même journal, ligne « historique » |
| Export JSON de 13 549 octets (clés `components`, `globals`, `graph`, `history`, `memory`, `messages`, `path`, `retrieval`, `variables`) | [Vérifié] | même journal, ligne « export » |
| Canevas vide : bloc « Récupération » relié à « Commencer », « Checklist » tant qu'aucune base | [Vérifié] | même journal, phase `blanc` |
| Mémoire : onglets « Messages » et « Configuration » ; souvenir apparu moins de 10 s après la réponse | [Vérifié] | même journal, lignes « page de la mémoire », « réponse avec mémoire », « messages de la mémoire » |
| Relecture d'une mémoire par « Retrieval » ; serveur MCP réel ; réponses en français par consignes traduites | [À tester] | non essayé |
| Croix d'un outil qui le retire sans confirmation | [Vérifié] | `captures/08-agents/scenario.log` ; commentaire de `fermer_panneau` dans le scénario |

### 4.11 Chapitre 11. Produire des synthèses automatiques

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Un « Compiler » appelle un opérateur, un opérateur a un gabarit : un seul type d'artefact par base | [Vérifié] et [Source] | captures `07-knowledge-compilation/` ; `docs/guides/knowledge_compilation/` |
| Gabarits intégrés (`knowledge_graph`, `mind_map`, `timeline`, `page_index`, `tree`, `wiki`, `session_essence`, `session_graph`) | [Vérifié] | `preuves-2026-11-09/compilation-builtins.json` |
| Limite de 20 minutes par appel au modèle ; variables `WIKI_*` et `STRUCTURE_*` sans effet | [Source] | `internal/ingestion/knowledge_compile/` |
| Configuration JSON d'un opérateur ; niveaux de « Mindmap » | [Vérifié] | `captures/07-knowledge-compilation/reperage-operateur-mindmap.txt` |
| « Découpeur par tokens » à 512 jetons par défaut ; un seul « Compiler » par pipeline ; « + » limité au dernier bloc | [Vérifié] | `captures/07-knowledge-compilation/scenario.log`, repérages |
| Ingestion et compilation « Graph » en 8 s ; 4 entités, 0 relation | [Vérifié] | même journal, lignes « ingestion et compilation », « artefact graph (API) » |
| « Tree » 142 s (1 nœud exact), « Timeline » 5 s (2 éléments, 1 relation), carte mentale exacte et complète | [Vérifié] | même journal ; `corpus/documents/cse-2025-10-14.md` |
| « Wiki » en échec après 3 min 0 s et 3 min 3 s, « PageIndex » après 2 min environ : « LLM response is not parseable JSON » ; heures des « Détails » en temps universel | [Vérifié] | `captures/07-knowledge-compilation/echec-wiki.log`, `echec-pageindex.log`, `scenario.log` |
| Étape secondaire illisible pour « Tree » (« tree: claim extraction skipped for batch ») | [Vérifié] | `echec-pageindex.log`, première ligne |
| Résultat variable d'un passage à l'autre (5 entités et 4 relations le 9, 4 et 0 le 11) | [Vérifié] | `essai-2026-11-09-compilation-knowledge_graph.log`, `scenario.log` |
| Modèle plus grand ou « Global rules » exigeant un JSON strict ; graphe enrichi par consignes | [À tester] | non essayé |
| Durée sur le corpus complet ou sur CPU : plusieurs minutes à plusieurs dizaines de minutes | [Estimation] | débit de 30 à 62 jetons/s relevé contre 15 à 17 sur CPU, `preuves-2026-11-09/vllm-extrait.log` |
| Pipeline créé par l'API : Compiler absent du canevas et retiré du brouillon | [Vérifié] | `captures/07-knowledge-compilation/incident-pipeline-demo.txt` |

### 4.12 Chapitre 12. Alimenter une base depuis une source externe

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Sitemap du site local refusé au test et à la synchronisation : « URL resolves to a non-public address (172.25.0.4), which is not allowed » ; site joignable (HTTP 200) depuis le conteneur | [Vérifié] | `essai-2026-11-09-sitemap-refus.log` ; `captures/09-sources-externes/scenario.log` |
| Journal : `error_count` 2, `total_docs_indexed` 0 ; première synchronisation dès l'enregistrement (journal lu 12 s après) | [Vérifié] | `captures/09-sources-externes/scenario.log` |
| Garde contre les adresses non publiques (boucle locale, réseaux privés, lien local) | [Source] | `internal/common/http.go` (`AssertURLSafe`), `internal/common/allow_private_host.go` |
| Avec `ALLOW_ANY_HOST=1` : test réussi, 2 pages en `.html.md`, 2 passages par page, `total_docs_indexed` 2 ; réglage remis à 0 et relu à 0 le 11 novembre | [Vérifié] | `essai-2026-11-09-sitemap-autorise.log` ; `captures/09-sources-externes/scenario.log` |
| Resynchronisation complète (`rebuild`) qui supprime d'abord les documents liés | [Source] ; [À tester] | `internal/service/connector.go` |
| Source suspendue après échec (statut « 5 ») et bouton « Resume » | [Estimation] ; [À tester] | `GET /api/v1/connectors` |
| Canaux de chat : non branchés (compte en ligne chez un tiers) | non couvert | carte de l'interface |

### 4.13 Chapitre 13. Gérer son compte, son équipe et ses clés

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Invitation d'une adresse sans compte refusée (« 102 user not found ») ; compte inscrit ajouté puis retiré, absent après rechargement | [Vérifié] | `captures/13-exploitation/02-invitation-refusee.txt`, `scenario.log` (lignes « ligne du membre », « confirmation du retrait », « membre encore présent après retrait : False ») |
| Invitation visible dans les « Équipes rejointes » du compte invité | [À tester] | non essayé |
| Fuseau du compte « Asia/Shanghai » par défaut ; heures en temps universel sur plusieurs pages ; effet du fuseau non essayé | [Vérifié] ; [À tester] | `captures/13-exploitation/04-profil.txt`, `scenario.log` |
| Console `/admin` réservée à `admin@ragflow.io` ; « Délai Expiré » pour le serveur, l'ingesteur et le synchroniseur alors que l'API répond | [Vérifié] | `captures/13-exploitation/scenario.log`, ligne « services » |
| Actions de « Utilisateurs » : « Nouvel utilisateur », « Statut », « Type d'utilisateur », corbeille, icône presse-papiers | [À tester] | non essayé |
| Changement de mot de passe par `PUT /users/{courriel}/password` | [Source] | `internal/admin/router.go` |
| « Déconnexion » de la console | [Vérifié] | même journal, ligne « après Déconnexion » |
| API d'administration sur le port 9381 | [Testée] | `essai-2026-11-09-admin.log`, `outils/ragflow/essai_admin.py` ; annexe [A4](A4-exploitation.md) |
| Clé d'API créée puis supprimée à la souris ; clé des scripts intacte | [Vérifié] | `captures/10-api-et-sdk/scenario.log` (lignes « clés avant », « clés après création », « clés après suppression ») |
| Fenêtre « Clé API » qui affiche les clés en clair | [Vérifié] | `captures/10-api-et-sdk/02-cles-api.txt` (clés remplacées à l'archivage) |
| Documentation intégrée en anglais, reprise de `docs/references/http_api_reference.md` ; codes `0`, `102`, `109` | [Source] ; [Vérifié] | `captures/10-api-et-sdk/01-page-api.txt` |
| Adresse affichée par « Serveur API » depuis le navigateur Windows | [À tester] | non essayé |
| Carte « Langfuse » | non couvert | aucun serveur Langfuse dans le banc |

### 4.14 Chapitre 14. Cas pratiques

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Assistant documentaire : base de 9 documents, 26 passages en 52 s ; assistant `top_n` 8, vecteurs 0,7 ; messages en français | [Testée] et [Vérifié] | `outils/ragflow/demo.py`, `demo-2026-11-09.log` |
| Conversations : contrat Batterix 2,3 s (212 euros HT, livraison sous 21 jours) ; objectifs 2026 2,0 s (55 M€, 70 embauches) ; audit en anglais 1,4 s (87 sur 100, défauts 0,3 %) | [Vérifié] | `demo-2026-11-09.log` |
| Base et assistant de démonstration ouverts dans l'interface | [Vérifié] | `captures/11-recettes/scenario.log` |
| Ingestion quotidienne : jour 1, 2 fichiers en 3 s ; jour 2, aucun ; jour 3, 1 fichier en 3 s ; aucun doublon ; question suivante en 1,7 s | [Testée] et [Vérifié] | `outils/ragflow/recette_ingestion.py`, `essai-2026-11-09-recette-ingestion.log` |
| Recette rejouée le 11 novembre dans « Manuel-Ingestion » : mêmes résultats, 3 documents | [Vérifié] | `captures/11-recettes/ingestion.log` |
| Suivi des fichiers modifiés sous le même nom par empreinte | [À tester] | non essayé |
| Lancement quotidien par `cron` (ligne donnée au chapitre) | [À tester] | ligne non exécutée ; seul le script l'a été, sur trois jours simulés |

### 4.15 Chapitre 15. En cas de problème

| Affirmation | Étiquette | Preuve |
|---|---|---|
| Connexion refusée : « 109 email and password do not match » ; code 109 = erreur d'authentification de l'API | [Vérifié] | `captures/14-depannage/scenario.log`, ligne « connexion refusée » |
| Page 404 : « Page not found, please enter a correct address. », bouton « Business » qui ramène à l'accueil | [Vérifié] | même journal, ligne « après « Business » » |
| Contexte réduit à 1 024 : « ERROR: prompt uses 2696 tokens… » en 3,4 s, sans citation ; remis à 16 384 aussitôt | [Vérifié] | `captures/14-depannage/scenario.log`, `02-erreur-de-contexte.txt`, `contexte.log` |
| 4 096 jetons suffisent, 3 072 échouent (21 sur 34) | [Vérifié] | `banc-2026-11-09-ctx4096.json`, `banc-2026-11-09-ctx3072.json`, `essai-2026-11-09-contexte-depassement.log` |
| Refus en anglais et message d'accueil anglais d'un assistant créé par l'API | [Vérifié] | `captures/14-depannage/scenario.log`, `preparation.log` |
| Santé sans compte : `curl http://127.0.0.1:9380/api/v1/system/healthz` renvoie `"status":"ok"` et HTTP 200 | [Testée] | `outils/ragflow/etat.sh` |
| `nettoyer.sh` en code 126 (droits perdus à l'extraction) | [Vérifié] | `essai-2026-11-09-reinstallation-essai1.log` |
| `du` ou `tar` refusés sur `donnees/ragflow/mysql` ; 1 Go de journal MySQL préalloué | [Vérifié] | `ressources-2026-11-09-*.txt`, `ressources-2026-11-09-apres-bancs.txt` |
| RAM de RAGFlow seul : 3,6 Gio au repos, 5,3 Gio en pointe | [Vérifié] | `ressources-2026-11-09-*.txt` |
| Sans GPU : 30 à 50 s par question à 4 096 jetons | [Estimation] | annexe [A2](A2-choisir-son-materiel-et-ses-modeles.md) |
| Données qui ne quittent pas la machine : configuration [Vérifié], journal du serveur sans téléchargement [Vérifié], absence d'envoi réseau [Estimation] (aucune capture du trafic) | mixte | `ports-2026-11-09.txt`, `preuves-2026-11-09/acces-sortants.txt` |
| Suppression complète par `outils/communs/nettoyer.sh ragflow` en 14 s, images gardées en cache | [Vérifié] | `essai-2026-11-09-reinstallation.log` |
| Erreurs de l'API et du SDK (404 de `Session.ask`, « doesn't own parsed file », générateur, `prompt_config`) | [Vérifié] | annexe [A3](A3-automatiser-par-l-api.md) ; `installation-2026-11-09-verif*.log`, `essai-2026-11-09-sdk-defauts.log` |

### 4.16 Chapitre 16. Glossaire

Définitions reprises du [glossaire de la série](../../glossaire.md) ; aucun essai propre.

## 5. Essais par l'API qui complètent les chapitres

Ces séquences ont servi à préparer le jeu de démonstration et à recouper les observations faites à la souris. Le reste de l'API et du SDK est dans l'annexe [A3](A3-automatiser-par-l-api.md).

### 5.1 Synthèses automatiques (chapitre 11)

Séquence suivie par `outils/ragflow/essai_compilation.py` [Testée] :

| Étape | Appel |
|---|---|
| Opérateur (groupe de gabarits) | `POST /api/v1/compilation-template-groups` avec un gabarit intégré (`kind`, `config`) |
| Pipeline | DSL du pipeline intégré `general` (`GET /api/v1/pipelines/general`) + nœud `Compiler` entre `Extractor` et `Tokenizer` ; `POST /api/v1/agents` avec `canvas_category: "dataflow_canvas"` |
| Publication | `POST /api/v1/agents/{pipeline}/publish` (donne la version) |
| Base en mode pipeline | `POST /api/v1/datasets` avec `parse_type: 2`, `pipeline_id`, `pipeline_version_id` |
| Ingestion | téléversement puis `POST /api/v1/datasets/{base}/documents/parse` |
| Suivi | `GET /api/v1/datasets/{base}/compilation/status?kind=mindmap` (ou `graph`, `timeline`) |
| Lecture | `GET /api/v1/datasets/{base}/artifacts/structure?kind=mindmap` (ou `graph`, `timeline`) |

Mesures, document : compte rendu du CSE (159 jetons) [Vérifié] :

| Artefact | Chemin | Durée totale (ingestion et compilation) | Résultat |
|---|---|---|---|
| Carte mentale, 1er essai | API, 9 novembre | environ 25 s (`last_completed_at`) | artefact lu à la main, non archivé |
| Carte mentale, 2e essai | API, 9 novembre | 40 s | 35 entités, 34 relations |
| Graphe de connaissances | API, 9 novembre | 15 s | 5 entités, 4 relations (« CSE »…) |
| Graphe de connaissances | souris, 11 novembre | 8 s | 4 entités, 0 relation |
| Arbre (Tree) | souris, 11 novembre | 142 s | 1 nœud résumé, exact |
| Frise (Timeline) | souris, 11 novembre | 5 s | 2 éléments, 1 relation |
| Wiki | souris, 11 novembre | échec après 3 min, deux fois | « LLM response is not parseable JSON » |
| Table des matières (PageIndex) | souris, 11 novembre | échec après 2 min environ | même erreur |

(`essai-2026-11-09-compilation-{mind_map-essai1,mind_map,knowledge_graph}.log` ; `captures/07-knowledge-compilation/scenario.log`) Les durées « souris » vont du clic sur « Enregistrer » du téléversement à la fin de la compilation lue par l'API de suivi, relevée toutes les 5 s.

- Piège du suivi : l'état passe de « idle » à « idle » ; la fin se lit au champ `last_completed_at` avec une file vide (`backlog` et `inflight` à 0). Le premier script attendait un état « completed » qui n'arrive jamais et a dû être arrêté à la main. [Vérifié] (`essai-2026-11-09-compilation-mind_map-essai1.log`)
- Un pipeline créé ainsi n'a pas de position pour le nœud `Compiler` dans le graphe du canevas (section 6). Ajouter le nœud aussi dans `dsl.graph.nodes` et `dsl.graph.edges` l'éviterait [À tester].

### 5.2 Agent (chapitre 10)

L'agent « Agent démo Vélanor » du jeu de démonstration a été créé le 9 novembre par l'API, depuis le même gabarit que le chapitre 10, par `outils/ragflow/essai_agent.py` (le script renseigne la base et le modèle du gabarit, deux `dataset_ids` et deux `llm_id`).

| Étape | Appel [Testée] |
|---|---|
| Créer l'agent | `POST /api/v1/agents` avec `{"title": "…", "dsl": …}` |
| Ouvrir une session | `POST /api/v1/agents/{agent}/sessions` avec `{}` |
| Poser une question | `POST /api/v1/agents/chat/completions` avec `{"agent_id", "session_id", "question", "stream": false}` |

Résultats [Vérifié] (`essai-2026-11-09-agent.log`) :

| Question | Durée | Réponse (début) |
|---|---|---|
| Qui est le directeur de production de Vélanor ? | 3,0 s | « According to the knowledge base, Julien Moreau is the production director at Vélanor. » |
| Quel est le plafond des pénalités de retard du contrat Batterix ? | 3,6 s | « …0.5% of the order amount per day of delay, capped at 8% of the order amount » |
| Combien de salariés compte Vélanor au 31 décembre 2025 ? (SDK) | 5,2 s | « …is **412 employees** (412 salariés) » |

- La réponse est dans `data.data.content`, les passages dans `data.data.reference`.
- Le SDK fonctionne pour les agents : `agent.create_session()` puis `next(iter(session.ask(question, stream=False)))`, à l'inverse des assistants de chat, pour lesquels `Session.ask` répond 404. [Vérifié] (même journal)
- `RAGFlow.create_agent` du SDK renvoie `None` : retrouver l'agent par `list_agents()`. [Source] (`sdk/python/ragflow_sdk/ragflow.py`)

### 5.3 Source « Sitemap » (chapitre 12)

Séquence suivie par `outils/ragflow/essai_sitemap.py` [Testée] :

| Étape | Appel |
|---|---|
| Créer le connecteur | `POST /api/v1/connectors` avec `{"name", "source": "sitemap", "config": {"sitemap_url": …}, "refresh_freq": 30}` |
| Le tester | `POST /api/v1/connectors/{id}/test` (l'interface appelle `POST /api/v1/connectors/sitemap/test` avant l'enregistrement) |
| Le lier à une base | `PUT /api/v1/datasets/{base}` avec `{"connectors": [{"id": …, "auto_parse": "1"}]}` |
| Suivre la synchronisation | `GET /api/v1/connectors/{id}/logs` (champs `error_msg`, `error_count`, `total_docs_indexed`) |

Le 9 novembre, la synchronisation a échoué après trois tentatives, et la base est restée vide (`essai-2026-11-09-sitemap-refus.log`). L'essai autorisé (`outils/ragflow/essai_sitemap_autorise.sh`) met `ALLOW_ANY_HOST=1` dans `donnees/ragflow/ragflow.env`, redémarre le serveur, synchronise, puis remet 0 et redémarre ; la valeur relue ensuite dans le conteneur est 0 (`docker exec rag-ragflow-server printenv ALLOW_ANY_HOST`). [Vérifié] (`essai-2026-11-09-sitemap-autorise.log`) Ce réglage vaut pour tout le serveur : les agents et leurs outils web peuvent alors joindre les machines du réseau local (attaque dite SSRF). [Source] (`internal/common/allow_private_host.go`)

### 5.4 Recherche et passages (chapitres 06 et 09)

- Passages : liste, correction, désactivation, ajout par `…/chunks` : annexe [A5](A5-fonctionnement-interne.md), section 9 (`outils/ragflow/essai_passages.py`).
- Applications de recherche : `GET /api/v1/searches` et `DELETE /api/v1/searches/{id}`, utilisés par `outils/ragflow/nettoyer_manuel.py`. [Vérifié] (`captures/15-recherche/nettoyage.log`)

## 6. Défauts de RAGFlow rencontrés

Comportements de RAGFlow v1.0.0 observés pendant les essais, avec leur preuve. Les contournements sont décrits dans les chapitres cités.

| Défaut | Effet | Chapitre | Preuve |
|---|---|---|---|
| « Confirmer » de « Modifier le segment » sans effet sur un passage de PDF modifié (aucune requête, fenêtre ouverte) ; le même geste est enregistré sur un passage Markdown | correction impossible à la souris pour un PDF | [06](../manuel/06-regler-la-lecture-des-documents.md) | [Vérifié] `captures/04-deepdoc/scenario.log` |
| Canevas qui n'affiche pas le « Compiler » d'un pipeline créé par l'API ; l'enregistrement automatique l'en retire du brouillon (version publiée intacte, brouillon remis par `PUT /api/v1/agents/{id}`) | synthèse perdue au prochain enregistrement | [11](../manuel/11-syntheses-automatiques.md) | [Vérifié] `captures/07-knowledge-compilation/incident-pipeline-demo.txt` |
| Croix d'un outil dans le panneau d'un bloc agent : retire l'outil sans confirmation, rendu définitif par l'enregistrement automatique | outil perdu | [10](../manuel/10-agents.md) | [Vérifié] `captures/08-agents/scenario.log` |
| Échap ferme toute la fenêtre « Créer une mémoire » | saisie perdue | [10](../manuel/10-agents.md) | [Vérifié] `JOURNAL.md`, entrée du 11 novembre 15:59 |
| Conversations non renommables (menu « … » limité à « Supprimer ») | titres figés sur la première question | [07](../manuel/07-poser-des-questions-et-lire-les-sources.md) | [Vérifié] `captures/05-assistants-et-citations/scenario.log` ; `conversation-dropdown.tsx` |
| Heures en temps universel (détails de tâche, historique des versions, « Date de téléversement ») ; fuseau du compte « Asia/Shanghai » par défaut ; heure de Paris dans le nom des versions | heures décalées d'une à deux heures | [11](../manuel/11-syntheses-automatiques.md), [13](../manuel/13-comptes-equipe-et-cles.md) | [Vérifié] `captures/13-exploitation/04-profil.txt`, `captures/08-agents/scenario.log`, `echec-wiki.log` |
| Console d'administration : « Délai Expiré » pour le serveur, l'ingesteur et le synchroniseur alors que l'API répond | état trompeur | [13](../manuel/13-comptes-equipe-et-cles.md) | [Vérifié] `captures/13-exploitation/scenario.log` |
| Fenêtre « Clé API » qui affiche chaque clé en entier, sans masque | fuite possible pendant un partage d'écran | [13](../manuel/13-comptes-equipe-et-cles.md) | [Vérifié] `captures/10-api-et-sdk/02-cles-api.txt` |
| Surlignage des résultats de recherche qui coupe les mots (« sa**larié** », « vers**ée** ») | affichage seulement | [09](../manuel/09-rechercher.md) | [Vérifié] capture `img/15-recherche/06-resultats.png` |
| Recherches connexes à moitié en anglais (question suivie de sa traduction) | affichage | [09](../manuel/09-rechercher.md) | [Vérifié] `captures/15-recherche/07-recherche-connexe.txt` |
| Restes de balises HTML autour des tableaux dans les passages affichés (`d>`, `le>`, « ption> ») | affichage, sans effet sur les réponses | [06](../manuel/06-regler-la-lecture-des-documents.md), [09](../manuel/09-rechercher.md) | [Vérifié] `captures/05-assistants-et-citations/20-test-resultats.txt`, `captures/15-recherche/06-resultats.txt` |
| Libellés non traduits (« Save », « Business », « Page not found… ») et messages par défaut d'un assistant créé par l'API en anglais | interface partiellement en anglais | [07](../manuel/07-poser-des-questions-et-lire-les-sources.md), [15](../manuel/15-en-cas-de-probleme.md) | [Vérifié] `JOURNAL.md` (lot 2) ; `captures/14-depannage/scenario.log`, `preparation.log` |
| Langue de l'interface liée au navigateur, pas au compte ; langue du compte changée par l'API sans effet sur l'affichage | interface en anglais à chaque nouveau navigateur | [03](../manuel/03-premiers-pas.md) | [Vérifié] `web/src/locales/config.ts` ; captures |
| Compte créé par l'API avec le mot de passe en clair : accepté par l'API, refusé dans le navigateur (le serveur compare `base64(mot de passe)`) | connexion impossible | [02](../manuel/02-installer-ragflow.md) | [Vérifié] `captures.py`, scénario `diag_connexion` ; `internal/common/password.go` |
| Mode « Agentic » instable avec le petit modèle : recherche parfois non lancée, réponse sans citation, environ 32 000 jetons d'entrée | moins juste et plus coûteux que « Naive » | [07](../manuel/07-poser-des-questions-et-lire-les-sources.md) | [Vérifié] `banc-2026-11-09-agentic.json`, `captures/06-agentic-rag/scenario.log` |
| Synthèses « Wiki » et « PageIndex » en échec avec `gemma4:e4b` (« LLM response is not parseable JSON »), document laissé à 0 passage | base non cherchable | [11](../manuel/11-syntheses-automatiques.md) | [Vérifié] `echec-wiki.log`, `echec-pageindex.log` |
| Suivi de compilation par l'API : état « idle » avant et après, sans état « completed » | un script qui attend « completed » ne finit jamais | section 5.1 | [Vérifié] `essai-2026-11-09-compilation-mind_map-essai1.log` |
| `reference.chunks` contient tous les passages donnés au modèle, pas seulement ceux cités | notation des citations à resserrer aux `[ID:n]` | [A3](A3-automatiser-par-l-api.md) | [Vérifié] `demo-2026-11-09.log` ; `outils/ragflow/banc.py` |
| SDK `ragflow-sdk` 1.0.0 : `Session.ask` en 404 pour un assistant ; `DataSet.parse_documents` rendu une fois avant la fin ; `Session.ask` générateur ; `prompt_config` objet ; poids des vecteurs lu à 0,3 ; `create_agent` qui renvoie `None` | contournements nécessaires | [A3](A3-automatiser-par-l-api.md) | [Vérifié] `installation-2026-11-09-verif.log`, `installation-2026-11-09-verif-essai1.log`, `essai-2026-11-09-sdk-defauts.log` ; [Source] `sdk/python/ragflow_sdk/ragflow.py` |
| Texte d'un passage HTML qui colle des éléments voisins (« après-venteDocument fictif.Quelle ») | sans effet observé sur la réponse | [A3](A3-automatiser-par-l-api.md) | [Vérifié] `exemples/ragflow/sorties_verifiees.txt`, exemple 03 |
| Compose officiel : ports sur `0.0.0.0`, mots de passe par défaut connus | exposition réseau si lancé tel quel | [02](../manuel/02-installer-ragflow.md), [A4](A4-exploitation.md) | [Source] `docker/docker-compose.yml`, `docker/.env` |
| Variables `WIKI_*` et `STRUCTURE_*` du `docker/.env` officiel lues par aucun code Go | réglages sans effet | [11](../manuel/11-syntheses-automatiques.md) | [Source] `internal/ingestion/knowledge_compile/` |
| Fournisseur « HuggingFace » marqué `TEXT RE-RANK` dans `conf/llm_factories.json`, mais son pilote Go répond « no such method: Rerank » ; aucun pilote ne parle le format `/rerank` de Text Embeddings Inference, que le compose officiel propose pourtant (profil `tei-cpu`) | reranker TEI inutilisable sans adaptateur | [A1](A1-evaluation-qualite-et-performances.md) | [Vérifié] `reranker-2026-11-11.log` (422) ; [Source] `internal/entity/models/huggingface.go` |
| Un reranker servi sous le nom `BAAI/bge-reranker-v2-m3` ou `maidalun1020/bce-reranker-base_v1` est pris pour un ancien reranker intégré : l'instance qui le sert n'est pas retenue | reranker choisi sans effet | [A1](A1-evaluation-qualite-et-performances.md) | [Source] `internal/service/chat.go`, `resolveCreateRerankID` ; [À tester] |
| `docker/migration.sh` ne sauvegarde pas les volumes Kvrocks et NATS de la 1.0 | sauvegarde officielle incomplète | [A4](A4-exploitation.md) | [Source] lecture du code au tag v1.0.0 |

## 7. Incidents des essais

Incidents dus au banc lui-même, et leur traitement. Le tableau complet est dans le [rapport RAGFlow](../../../RAPPORT-ragflow.md), section « Incidents ».

| Incident | Traitement | Preuve |
|---|---|---|
| Droits d'exécution perdus à l'extraction de l'archive du kit (`nettoyer.sh` en code 126) | `chmod +x`, cycle rejoué | `essai-2026-11-09-reinstallation-essai1.log` |
| Notation des citations trop large dans la première série du banc | notation resserrée aux `[ID:n]`, série rejouée, même résultat | `essai-2026-11-09-serie-banc-notation-large.log`, `essai-2026-11-09-serie-banc.log` |
| Deux réglages mal relevés par `banc.py` (contexte, poids des vecteurs) | corrigés dans les JSON avec une note, script corrigé | `JOURNAL.md` |
| `vllm-central` en redémarrage en boucle le matin du 11 novembre (mémoire de la carte prise par un autre projet) | question réelle du chapitre 04 rejouée après remise en service | `preuves-2026-11-11/llm-service-reparation.log` ; `JOURNAL.md` |
| Première passe du scénario `cles` sans gestion de la confirmation de suppression | clé d'essai supprimée par l'API | `captures/10-api-et-sdk/nettoyage.log` |
| Brouillon du pipeline de démonstration touché par un repérage | remis depuis la version publiée par `PUT /api/v1/agents/{id}` | `captures/07-knowledge-compilation/incident-pipeline-demo.txt` |
| Reranker TEI : `--max-batch-tokens` par défaut (16 384), échauffement à 13,6 Go de RAM puis redémarrages en boucle | conteneur arrêté, relancé avec 2 048 et une limite de 6 Go | `reranker-2026-11-11.log` |
| Un commit passé avec 1 point de `verifier_docs.py` | corrigé au commit suivant ; depuis, chaque commit dépend du code de sortie du vérificateur | `JOURNAL.md` |

## 8. Ce qui n'a pas été vérifié

| Sujet | Raison |
|---|---|
| Mise à jour de version | aucune version plus récente que v1.0.0 le jour des essais |
| Reranking (banc avec et sans reranker, branchement à la souris) | TEI incompatible avec les pilotes de RAGFlow ; `vllm-rerank` préparé mais non démarré faute de VRAM ; essai reporté au nouveau service de modèles (llama.cpp derrière LiteLLM) |
| Second modèle (`ministral-3:3b`) et modèle de moins de 3 milliards de paramètres | LLM-Service en branche `service-vllm` sert un seul modèle de réponse, partagé |
| Profil A sans carte graphique | machine d'essai avec GPU : chiffres en [Estimation] à partir des mesures CPU du socle (`outils/resultats/socle/`), annexe [A2](A2-choisir-son-materiel-et-ses-modeles.md) |
| Contexte entre 3 072 et 4 096 jetons | 4 096 suffit, 3 072 échoue ; valeurs intermédiaires non essayées |
| Synthèses « Wiki » et « PageIndex » réussies | échec du petit modèle ; modèle plus grand non servi |
| Gabarit « Picture », « Enable vision enhancement », analyseurs PDF externes, OCR externe | aucun modèle `image2text` ni service externe déclaré |
| Lecture à voix haute, micro, recherche web | modèles TTS et Speech2txt non déclarés dans les assistants ; recherche web liée à un compte en ligne |
| Modèles d'agents qui demandent Internet, serveur MCP réel, relecture d'une mémoire par « Retrieval », consignes d'agent traduites, « Decision model » | service en ligne ou essai non mené |
| Canaux de chat, sources de données en ligne | compte en ligne chez un tiers, hors périmètre |
| Resynchronisation complète (`rebuild`), bouton « Resume » d'une source | non essayés |
| Effet de la langue « English » de la base sur la recherche d'un corpus français | non essayé |
| Actions de la console d'administration sur les comptes, invitation vue par le compte invité, effet du fuseau du compte | non essayés |
| Carte « Langfuse » de la page « API » | aucun serveur Langfuse |
| Absence d'envoi réseau | aucune capture du trafic : [Estimation] |
| Ouverture de RAGFlow à d'autres postes (autre adresse, inscription fermée, proxy HTTPS) | hors périmètre (ports sur `127.0.0.1` seulement) |

La liste des points ouverts et des décisions en attente est tenue dans la [page d'accueil du manuel](../README.md) et dans le [rapport RAGFlow](../../../RAPPORT-ragflow.md).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Un fichier de preuve cité est introuvable | chemin relatif à `outils/resultats/ragflow/` omis | chercher le nom dans `outils/resultats/ragflow/` et ses sous-dossiers `captures/`, `preuves-2026-11-09/`, `preuves-2026-11-11/` |
| Un texte de capture ne correspond plus à l'écran | objets d'essai supprimés après la capture, ou interface d'une autre version | rejouer le scénario par `outils/communs/captures/lancer.sh outils/ragflow/captures/<scénario>.py <nom>` |
| Un scénario rejoué échoue sur un objet déjà présent | objets « Manuel-… » d'un passage précédent | `uv run python outils/ragflow/nettoyer_manuel.py`, puis rejouer |
| Un chiffre du banc diffère d'un nouveau passage | petit modèle non déterministe, ou réglages différents | comparer le champ `config` du JSON du banc ; voir l'annexe [A1](A1-evaluation-qualite-et-performances.md) |
| `verifier_docs.py` signale des points | lien, image, ton ou gabarit non conformes | corriger jusqu'à 0 point avant tout commit |

## Sources

- Mission : `kit/PROMPT.md` (fiche `kit/fiches/02-ragflow.md`) ; journal : `JOURNAL.md` ; bilan : [RAPPORT-ragflow.md](../../../RAPPORT-ragflow.md)
- Corpus et questions : `corpus/MANIFEST.json`, `corpus/questions.json`, `outils/communs/generer_corpus.py`, `outils/communs/generer_audio.py`
- Banc : `outils/communs/banc/`, `outils/ragflow/banc.py`, `outils/ragflow/serie_banc.sh` ; résultats `outils/resultats/ragflow/banc-2026-11-09-*.json` et `.md`
- Captures : `outils/communs/captures/annoter.py`, `outils/communs/captures/lancer.sh`, `outils/ragflow/captures/` ; textes et déroulés : `outils/resultats/ragflow/captures/`
- Scripts d'essai et journaux : `outils/ragflow/`, `outils/resultats/ragflow/` ; preuves complémentaires de la relecture : `outils/resultats/ragflow/preuves-2026-11-09/`
- Relecture du compose et du code : [`relecture.md`](../../../outils/resultats/ragflow/relecture.md) ; versions : [`versions-2026-11-09.json`](../../../outils/resultats/ragflow/versions-2026-11-09.json)
- Fichiers du dépôt officiel cités par les anciens manuels : `internal/agent/templates/compiler.json`, `docs/guides/knowledge_compilation/` (synthèses) ; `internal/syncer/connector/sitemap.go`, `internal/common/http.go`, `docs/guides/.../data_source_configuration.md` (sources) ; `internal/handler/agent.go`, `sdk/python/ragflow_sdk/` (agents) ; texte de la page « Configuration » d'une base : `outils/resultats/ragflow/captures/carte/09-base-configuration.txt` (modèle d'embedding et gabarit modifiables après la création, [Vérifié])
- Code et documentation de RAGFlow au tag v1.0.0 (commit `db1cd5929a7885a3074547791f5ecc4d2f891739`) : https://github.com/infiniflow/ragflow ; https://ragflow.io/docs/
