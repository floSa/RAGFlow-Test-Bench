# A2. Choisir son matériel et ses modèles

> **Objet** : ce qui consomme la mémoire et le temps, configurations minimales sans et avec carte graphique (profils A et B), taille de contexte par profil, volume de documents utilisable, temps d'attente, et fiche technique de la version essayée.
> **Prérequis** : chapitre [01. Découvrir RAGFlow](../manuel/01-decouvrir-ragflow.md) (version courte de cette annexe) ; annexe [A1](A1-evaluation-qualite-et-performances.md) pour les résultats du banc.
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), service LLM central depuis le 12 novembre 2026 (LiteLLM v1.109.0, llama-swap v272, llama.cpp build 12282 : `chat` Qwen3.5-4B Q4_K_M, `embed` bge-m3 Q8_0, `rerank` bge-reranker-v2-m3 Q8_0 sur la carte graphique, `transcribe` faster-whisper-small sur le processeur) ; historique du 9 au 11 novembre : LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b` quantifié w4a16, `bge-m3`) ; contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré les 9, 11 et 12 novembre 2026 sur la machine d'essai (profil B : Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré, avec son raisonnement ; [À tester] non documenté et non essayé.
> **Précautions** : seul le profil B (avec carte graphique) a été mesuré ; le profil A (sans carte graphique) est calculé à partir des mesures CPU du socle de la série, pas essayé avec RAGFlow. Sur 16 Go de mémoire, arrêter les autres solutions de la série avant de démarrer RAGFlow.

## Sommaire

1. [Ce qui consomme la mémoire et le temps](#1-ce-qui-consomme-la-mémoire-et-le-temps)
2. [Profil B, avec carte graphique NVIDIA (mesuré)](#2-profil-b-avec-carte-graphique-nvidia-mesuré)
3. [Profil A, sans carte graphique (estimé)](#3-profil-a-sans-carte-graphique-estimé)
4. [Taille de contexte par profil](#4-taille-de-contexte-par-profil)
5. [Volume de documents utilisable](#5-volume-de-documents-utilisable)
6. [Modèles plus légers et second modèle](#6-modèles-plus-légers-et-second-modèle)
7. [Fiche technique de la version essayée](#7-fiche-technique-de-la-version-essayée)
8. [Serveur de modèles de la machine d'essai (LLM-Service)](#8-serveur-de-modèles-de-la-machine-dessai-llm-service)
9. [Dépannage](#dépannage)
10. [Sources](#sources)

## 1. Ce qui consomme la mémoire et le temps

RAGFlow ne contient aucun modèle d'IA : il les appelle sur LLM-Service, service à part. La machine fait donc tourner deux ensembles : l'application (six conteneurs : serveur et DeepDoc, moteur de recherche Elasticsearch, base de données, stockage de fichiers, cache, file de tâches ; détail dans l'annexe [A5](A5-fonctionnement-interne.md)) et le service de modèles.

| Mesure | Valeur |
|---|---|
| RAM de l'application au repos / en pointe | 3 730 Mio / 5 394 Mio, soit 3,6 / 5,3 Gio (Elasticsearch 2,7 Gio, serveur et DeepDoc 1,9 Gio) |
| RAM du service central (hors application), 12 novembre | `llm-swap` (llama.cpp : `chat`, `embed`, `rerank`) 6,2 à 6,8 Gio, `llm-speaches` (`transcribe`) 1,4 Gio, `llm-central` (LiteLLM) 0,7 Gio |
| VRAM, 12 novembre | 8 235 à 8 440 Mio occupés sur 16 380 avec le trio `chat` + `embed` + `rerank` chargé, bureau Windows compris (part de chacun non séparable) |
| Historique, 9 novembre : RAM et VRAM de l'ancienne pile | `vllm-central` 6,5 Gio, `vllm-embed` 4,1 Gio ; 15 247 Mio de VRAM sur 16 380 (`vllm-central` réserve 80 %, `vllm-embed` 5 %) |
| Indexation du corpus (9 documents, 1 Mo, 26 passages) | 52 à 56 s (71 s au premier essai de l'adaptateur) |
| OCR d'un scan | 4,7 s par page |
| Question | 7,8 s en médiane et 50 à 58 s au 95e centile avec `chat` (réflexion activée) ; 1,3 s en médiane avec `gemma4:e4b` sur vLLM (historique) ; 1 841 jetons d'entrée et 54 de sortie pour une question type (historique) |
| Débit de génération de vLLM (historique, 9 novembre) | 30 à 62 jetons/s selon la charge (journal de `vllm-central`) |

[Vérifié] (`outils/resultats/ragflow/ressources-llm-central-2026-11-12.txt`, `essai-2026-11-12-serie-banc.log`, `banc-2026-11-12-*.json`, `outils/resultats/ragflow/ressources-2026-11-09-*.txt`, `banc-2026-11-09-defaut.json`, `essai-2026-11-09-passages.log`, `outils/resultats/ragflow/preuves-2026-11-09/vllm-extrait.log`, `outils/resultats/ragflow/preuves-2026-11-09/textes-captures/02-conversation.txt`)

En langage courant : l'application seule occupe un peu plus de 5 Go de mémoire pendant l'ajout de documents, dont la moitié pour le moteur de recherche ; les modèles s'y ajoutent (environ 8,5 Go de RAM et 8 Go de mémoire graphique pour le service central de la machine d'essai, environ 5 Go sur processeur avec un contexte de 4 096 jetons). L'OCR tourne sur le processeur dans les deux profils. La mémoire par service et l'installation détaillée sont dans l'annexe [A4](A4-exploitation.md).

## 2. Profil B, avec carte graphique NVIDIA (mesuré)

| Rubrique | Valeur |
|---|---|
| Carte | RTX 4060 Ti 16 Go ; 8,2 à 8,4 Go occupés avec le trio du service central (`chat`, `embed`, `rerank`) et le bureau Windows : il reste près de 8 Go libres ; minimum estimé 8 Go de VRAM pour le trio [Estimation] |
| Processeur, RAM, disque | 6 cœurs (12 fils) ; 32 Go dans WSL, dont environ 16 Gio utilisés (application 5,4 Gio en pointe, service central environ 8,5 Gio) ; 4,3 Go pour l'application (images et données) plus les modèles |
| Modèles | `chat` = Qwen3.5-4B Q4_K_M (réflexion activée par défaut, vision), `embed` = bge-m3 Q8_0, `rerank` = bge-reranker-v2-m3 Q8_0, tous trois par llama.cpp sur la carte ; `transcribe` = faster-whisper-small sur le processeur |
| Contexte | 16 384 jetons par requête servis pour `chat` (4 requêtes en parallèle), 8 192 pour `embed` et `rerank` ; 16 384 déclarés dans RAGFlow ; 4 096 suffisait sur ce corpus avec l'ancien modèle, 3 072 ne suffisait plus |
| Réglages du service | `llama-server -ngl 99 -np 4 --kv-unified --kv-unified-per-slot 16384 -ctk q8_0 -ctv q8_0 -fa on --reasoning on` (chat) ; géré à part, lecture seule |
| Réglages de RAGFlow | gabarit General, `top_n` 8, poids des vecteurs 0,7, sans reranker |
| Résultat | 34/34, médiane 7,8 s (avec reranker : 34/34, 8,8 s) |
| Temps d'attente | 8 s par question en médiane, jusqu'à une minute pour les plus longues (réflexion du modèle) ; ajout des 9 documents en environ une minute |
| Historique (9 novembre) | `gemma4:e4b` w4a16 et `bge-m3` sur vLLM, 15,2 Go de VRAM pour deux modèles (`--max-model-len 32768`, `--gpu-memory-utilization 0.8`) : 34/34 en 1,36 s de médiane ; pas de place pour un reranker |

[Vérifié] (`outils/resultats/ragflow/ressources-llm-central-2026-11-12.txt` : arguments de lancement relevés dans llama-swap ; bancs de l'annexe [A1](A1-evaluation-qualite-et-performances.md), section 2.1 ; historique : `outils/resultats/ragflow/preuves-2026-11-09/vllm-extrait.log`)

## 3. Profil A, sans carte graphique (estimé)

Portable Intel Core Ultra 7 255H, 15,3 Go dans WSL, LLM-Service `service-ollama` sur CPU.

| Rubrique | Valeur | Calcul |
|---|---|---|
| Processeur | 8 cœurs récents ; 8 fils de calcul pour Ollama (`LLAMA_ARG_THREADS=8`) | mesure du socle de la série |
| RAM | 16 Go dans WSL au minimum : application 5,3 Gio en pointe + Ollama (`qwen3:4b-instruct` chargé : 3,9 Go à 4 096 jetons, 7,5 Go à 16 384 ; plus `bge-m3`) + système | somme des mesures ; à 16 384 jetons, 15,3 Go dans WSL ne suffisent plus : garder 4 096 ou réduire `MEM_LIMIT` d'Elasticsearch [À tester] |
| Disque | 10 Go libres : 3,1 Go d'images + 1,2 Go de données à vide + environ 4 Go de modèles | mesures |
| Modèles | `qwen3:4b-instruct` (réponses, 4 milliards de paramètres, 2,5 Go), `bge-m3` (embedding, 1,2 Go, multilingue) | modèles de la série sur CPU |
| Contexte | 4 096 conseillé sur ce profil (`OLLAMA_CONTEXT_LENGTH`) | prompt de 1 841 à 3 301 jetons |
| Temps par question | 30 à 50 s à 4 096 jetons ; 55 à 95 s à 16 384 | lecture du prompt de `qwen3:4b-instruct` sur CPU : 67 jetons/s à 4 096, 36 jetons/s à 16 384 ; 1 841 à 3 301 jetons, soit 27 à 49 s (51 à 92 s) ; plus 60 jetons générés à 15 à 17 jetons/s (environ 4 s) ; moins quand Ollama réutilise le début du prompt |
| Indexation du corpus | plusieurs minutes pour une dizaine de documents | embedding sur CPU au lieu du GPU ; OCR inchangé (déjà sur CPU) |

[Estimation] (mesures CPU du socle : `outils/resultats/socle/mesures-2026-11-08-passe1.log` pour `qwen3:4b-instruct`)

- Sur 16 Go, il faut arrêter les autres solutions de la série avant de démarrer RAGFlow : Elasticsearch seul occupe 2,5 à 2,7 Gio [Vérifié] ; le reste est [Estimation].
- Sans GPU, compter 30 à 50 s par question à 4 096 jetons : utilisable pour des questions ponctuelles, pas pour une conversation [Estimation]. Le mode « Agentic », avec environ 32 000 jetons d'entrée, demanderait plusieurs minutes par question [Estimation].
- Déclaration du fournisseur « Ollama » à l'adresse `http://ollama-central:11434` : chemin décrit au chapitre [03](../manuel/03-premiers-pas.md), non essayé avec RAGFlow [À tester].

## 4. Taille de contexte par profil

RAGFlow n'envoie pas `num_ctx` : il borne la réponse à « contexte déclaré − jetons du prompt » (détail et mesures à 4 096, 3 072 et 512 dans l'annexe [A1](A1-evaluation-qualite-et-performances.md), section 9). [Source] (`internal/service/chat_pipeline.go`)

| Profil | Contexte servi | « Tokens maximum » déclaré dans RAGFlow | Raison |
|---|---|---|---|
| B (service central, llama.cpp) | 16 384 par requête (`--kv-unified-per-slot`) | 16 384 | référence de la série ; égal à la taille servie [Vérifié] ; avec l'ancien vLLM (32 768 servis), 4 096 suffisait sur ce corpus [Vérifié] |
| A (Ollama) | `OLLAMA_CONTEXT_LENGTH` du serveur | 4 096 | la lecture du prompt est deux fois plus rapide qu'à 16 384 et le modèle tient dans 15,3 Go [Estimation] |

Jamais moins de 4 096 : le prompt monte à 3 301 jetons avec 6 passages, davantage avec « Top N » 8 ; à 3 072, une réponse sur trois est une erreur. [Vérifié] (`banc-2026-11-09-ctx3072.json`)

## 5. Volume de documents utilisable

Le volume de documents n'est pas limité par le contexte : seuls les `top_n` passages retenus (6 à 8) vont au modèle. La limite est le temps d'indexation et la mémoire d'Elasticsearch. [Vérifié] (fonctionnement du banc)

- À 53 s pour 1 Mo et 13 pages, un fonds de 1 000 pages de PDF texte demanderait de l'ordre d'une heure d'indexation sur le profil B, davantage s'il est scanné (4,7 s par page d'OCR, soit environ 80 minutes pour 1 000 pages) [Estimation].
- En langage courant : environ une minute par mégaoctet de documents, cinq secondes par page scannée. [Estimation] à partir des mesures de la section 1.
- Le nombre de documents d'une base ne ralentit pas les réponses de façon visible sur ce corpus. [Vérifié] (bancs de l'annexe [A1](A1-evaluation-qualite-et-performances.md))

## 6. Modèles plus légers et second modèle

- Un modèle plus léger que le modèle principal (moins de 3 milliards de paramètres) n'a pas pu être essayé : il aurait fallu changer le modèle servi par LLM-Service, partagé avec d'autres applications. Plancher de qualité [À tester].
- Second modèle : la fiche prévoit `ministral-3:3b` ; non essayé. Le service central sert aussi `gemma-4-e4b` sous son nom brut : banc à faire [À tester].
- Reranker sur la même carte que les deux autres modèles : avec le service central (llama.cpp, modèles GGUF quantifiés), le trio tient sur 16 Go avec le bureau Windows actif (8,2 à 8,4 Go occupés) [Vérifié] (`ressources-llm-central-2026-11-12.txt`). Historique : le 11 novembre, avec vLLM (`vllm-central` 11,06 Gio de poids et 0,7 Go de cache, `vllm-embed` 1,06 Gio), la VRAM libre est restée entre 211 et 461 Mio, alors qu'un `vllm-rerank` aurait demandé environ 1,6 Go [Vérifié] pour la VRAM libre, [Estimation] pour le besoin (`outils/resultats/ragflow/reranker-2026-11-11.log`) ; sur processeur, le reranker TEI démarre mais RAGFlow ne sait pas l'appeler (annexe [A1](A1-evaluation-qualite-et-performances.md), section 7).

## 7. Fiche technique de la version essayée

Relevé GitHub du 9 novembre 2026 [Vérifié] (`outils/resultats/ragflow/identite-github-2026-11-09.json`) :

| | |
|---|---|
| Dépôt | https://github.com/infiniflow/ragflow |
| Site | https://ragflow.io |
| Licence | Apache-2.0 : libre, usage commercial autorisé ; gratuit, aucun abonnement |
| Popularité | 93 880 étoiles, 11 278 forks sur GitHub |
| Activité | très forte : 2 763 modifications sur les 90 derniers jours, 925 contributeurs |
| Ancienneté | projet créé en décembre 2023 ; version 1.0.0 publiée le 6 novembre 2026, réécrite en Go |

Précisions sur les fonctions, en complément du tableau du chapitre [01](../manuel/01-decouvrir-ragflow.md) [Vérifié] sauf mention (`outils/resultats/ragflow/relecture.md` et essais des chapitres) :

| Fonction | Réponse |
|---|---|
| Formats acceptés | PDF, Word, Excel, PowerPoint, texte, Markdown, HTML, courriels, EPUB |
| Calcul des embeddings sur la machine | Oui |
| Reranking | Partiel : aucun modèle fourni ; essayé avec le reranker du service central (annexe [A1](A1-evaluation-qualite-et-performances.md), section 7.4) |
| Transcription audio sur la machine | Oui, avec un modèle de transcription servi à part (`transcribe` du service central) |
| Documents scannés | Oui, environ 5 secondes par page ; quelques confusions de caractères à corriger à la main |
| Agents à partir de modèles prêts à l'emploi | Oui, 19 modèles ; consignes en anglais |
| Wikis, tables des matières automatiques (« Wiki », « PageIndex ») | En échec avec `gemma4:e4b` (chapitre [11](../manuel/11-syntheses-automatiques.md)) ; non rejoué avec `chat` |
| Installation | Docker, six conteneurs : l'application, un moteur de recherche, une base de données, un stockage de fichiers, un cache, une file de tâches |
| Interface en français | Oui, par le sélecteur de langue ; la page de connexion reste en anglais au premier lancement |
| API pour automatiser | Oui, complète ; le module Python a deux défauts contournés (annexe [A3](A3-automatiser-par-l-api.md)) |
| Fonctionnement hors ligne | Oui en principe : aucun téléchargement mentionné dans le journal du serveur ; le trafic réseau n'a pas été enregistré [À tester] |
| Sauvegarde et restauration | Oui, par copie des données, application arrêtée (une demi-minute ; annexe [A4](A4-exploitation.md)) |

## 8. Serveur de modèles de la machine d'essai (LLM-Service)

Le manuel ne fait installer aucun serveur de modèles : RAGFlow se branche sur un serveur existant (chapitre [03](../manuel/03-premiers-pas.md)). Cette section décrit, à titre d'exemple, celui de la machine d'essai.

**LLM-Service** est un dépôt distinct (privé, accès à demander à son propriétaire), partagé par plusieurs applications et géré à part : ce dépôt ne l'arrête ni ne le modifie. Depuis le 12 novembre 2026, il tourne en **service LLM central** (branche `service-llamacpp`) : une passerelle LiteLLM, `llm-central`, seul point d'entrée (`http://llm-central:8080/v1` sur le réseau `llm-net`, `http://127.0.0.1:8080/v1` depuis l'hôte, clé obligatoire), devant `llm-swap` (llama-swap et llama.cpp sur la carte graphique : `chat`, `embed`, `rerank`) et `llm-speaches` (Speaches sur le processeur : `transcribe`). [Vérifié] (`outils/resultats/ragflow/versions-llm-central-2026-11-12.txt`)

| Action | Commande | Statut |
|---|---|---|
| Démarrer (profil carte graphique), s'il est arrêté | `~/mes_projets/Projet-IA/LLM-Service/scripts/demarrer.sh` | [Testée] le 12 novembre 2026 après un redémarrage de la machine : chat, embed et rerank chargés en 12 s |
| Vérifier depuis ce dépôt | `outils/communs/llm_central_sante.sh --essai` | [Testée] : réponses de `chat`, `embed` (1 024 dimensions), `rerank`, `transcribe` |
| Clé | `LLM_CENTRAL_KEY` dans le `.env` de ce dépôt (copie de `.env.example`), valeur fournie par le responsable du service | jamais affichée ni commitée |

Ports du service : `127.0.0.1:8080` (passerelle) et `127.0.0.1:8081` (diagnostic de llama-swap), liés à la machine seule. [Vérifié] (`docker ps`)

### 8.1 Historique : ancienne pile vLLM (9 au 11 novembre 2026)

Les scripts `outils/communs/llm_service.sh`, `llm_service_vllm.sh`, `voix.sh` et les branches `service-ollama` / `service-vllm` sont historiques : ne pas les lancer. Ce qui suit décrit l'ancienne pile, dont viennent les mesures datées du 9 au 11 novembre.

**LLM-Service** est un dépôt distinct (privé, accès à demander à son propriétaire), partagé par plusieurs applications. Les scripts du banc le cherchent dans `~/mes_projets/Projet-IA/LLM-Service` (autre emplacement : variable `LLM_SERVICE_DIR`). Deux branches : `service-vllm` avec carte graphique NVIDIA (vLLM, serveur de modèles pour carte graphique ; celle des essais) et `service-ollama` sans carte graphique (Ollama, serveur de modèles qui tourne aussi sur processeur ; non essayé avec RAGFlow) [Vérifié] pour la première, [À tester] pour la seconde.

```bash
git clone https://github.com/floSa/LLM-Service.git ~/mes_projets/Projet-IA/LLM-Service
cd ~/mes_projets/Projet-IA/LLM-Service
git checkout service-vllm      # sans carte graphique : git checkout service-ollama
cp .env.example .env
nano .env                      # éditeur de texte du terminal : Ctrl+O enregistre, Ctrl+X quitte
make up                        # make lance la commande « up » définie dans le Makefile du dépôt
```

Réglages du `.env` utilisés pour les essais (branche `service-vllm`) [Vérifié] :

```text
VLLM_EMBED_MODEL=BAAI/bge-m3
VLLM_EMBED_SERVED_NAMES=bge-m3 BAAI/bge-m3
VLLM_EXTRA_ARGS=--kv-cache-memory=700000000
```

La troisième ligne limite la mémoire que le serveur de réponses réserve sur la carte graphique quand un autre programme l'occupe déjà : sans elle, `vllm-central` a redémarré en boucle le 11 novembre 2026 (« No available memory for the cache blocks », 2,6 Go déjà pris par un autre programme) [Vérifié].

Au premier démarrage, le service télécharge environ 12 Go de modèles, puis prépare la carte graphique pendant une minute environ ; les démarrages suivants prennent environ deux minutes. Deux conteneurs passent à « (healthy) » : `vllm-central` (`gemma4:e4b`, adresse `http://vllm-central:8000/v1`) et `vllm-embed` (`bge-m3`, adresse `http://vllm-embed:8000/v1`) [Vérifié]. Vérification depuis le dépôt du banc : `outils/communs/llm_service_vllm.sh` (version vLLM) ou `outils/communs/llm_service.sh` (version Ollama, `qwen3:4b-instruct` et `bge-m3`, adresse `http://ollama-central:11434`) [Testée] pour le premier.

LLM-Service publie ses ports (8001 et 8002) pour toutes les machines du réseau, contrairement à RAGFlow : sur un réseau partagé, le vérifier dans son `docker-compose.yml`.

Le serveur de transcription de la machine d'essai, `rag-speaches` (Speaches 0.8.3 sur processeur, `Systran/faster-whisper-small`), est démarré par `outils/communs/voix.sh` (chapitre [02](../manuel/02-installer-ragflow.md), étape 5).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| La machine ralentit fortement pendant une indexation | Elasticsearch (2,7 Gio) et le modèle se disputent la mémoire | arrêter les autres solutions ; garder 4 096 jetons sur le profil A |
| Réponses de 30 s ou plus sans carte graphique | lecture du prompt sur CPU | normal sur le profil A ; garder « Naive » et 4 096 jetons |
| Erreur du serveur de modèles sur une longue question | « Tokens maximum » déclaré plus grand que le contexte servi [Estimation] | déclarer une taille inférieure ou égale à celle du serveur |
| Pas de place sur la carte pour un troisième modèle (reranker) avec vLLM (historique) | modèle de réponse et embedding déjà chargés, programmes Windows sur la même carte | service central llama.cpp (modèles GGUF quantifiés), où le trio tient ; voir la section 6 |
| Le service central ne répond pas | arrêté (aucun démarrage automatique au lancement de la machine) | `~/mes_projets/Projet-IA/LLM-Service/scripts/demarrer.sh`, puis `outils/communs/llm_central_sante.sh --essai` |
| Mémoire graphique saturée au démarrage de LLM-Service (ancienne pile vLLM) | autre conteneur sur la carte, ou mémoire prise par Windows | voir le `.env` local de LLM-Service (`VLLM_EXTRA_ARGS`) et l'annexe [A4](A4-exploitation.md) |

## Sources

- Mesures de ressources : `outils/resultats/ragflow/ressources-2026-11-09-*.txt` ; VRAM avec reranker : `outils/resultats/ragflow/reranker-2026-11-11.log` ; journal vLLM : `outils/resultats/ragflow/preuves-2026-11-09/vllm-extrait.log`
- Bancs : `outils/resultats/ragflow/banc-2026-11-09-*.json` ; [banc par défaut](../../../outils/resultats/ragflow/banc-2026-11-09-defaut.md)
- Socle CPU : `outils/resultats/socle/mesures-2026-11-08-passe1.log` ; diagnostic : `outils/resultats/machine/diagnostic-2026-11-09.json`
- Identité du projet : [relevé GitHub](../../../outils/resultats/ragflow/identite-github-2026-11-09.json) ; [relecture du code](../../../outils/resultats/ragflow/relecture.md) ; [résultats des essais](../../../outils/resultats/ragflow/)
- Code au tag v1.0.0 : `internal/service/chat_pipeline.go` ; https://ragflow.io/docs/
