# A7. Bascule vers le service LLM central

> **Objet** : brancher RAGFlow sur le service LLM central (LLM-Service, LiteLLM) à la place de l'ancienne pile `vllm-central` / `vllm-embed` / `rag-speaches`, depuis l'interface web.
> **Prérequis** : le service tourne (géré à part, jamais démarré par ce dépôt) ; la clé du service est dans `.env` (`LLM_CENTRAL_KEY`) ; RAGFlow joint le réseau `llm-net`.
> **Statut des informations** : [Vérifié] requêtes réelles du 11 novembre 2026 depuis `rag-ragflow-server` et l'hôte (journal : `outils/resultats/ragflow/essai-llm-central-2026-11-11.log`) ; [Source] code de RAGFlow v1.0.0 (`sources/ragflow/conf/models/`, `internal/entity/models/`) ; [À tester] les clics de l'interface, non rejoués.

## 1. Le service

| Élément | Valeur |
|---|---|
| URL depuis un conteneur du réseau `llm-net` | `http://llm-central:8080/v1` (résolution DNS vérifiée depuis `rag-ragflow-server`) |
| URL depuis l'hôte | `http://127.0.0.1:8080/v1` |
| Clé | obligatoire, en-tête `Authorization: Bearer <clé>` ; valeur dans `.env` (non suivi par git) |
| `chat` | Qwen3.5-4B, vision, réflexion activée par défaut, 16 384 jetons par requête |
| `embed` | bge-m3 Q8_0 GGUF, 1 024 dimensions |
| `rerank` | bge-reranker-v2-m3, scores bruts non bornés (observés de -11 à +9) |
| `transcribe` | faster-whisper-small, `/v1/audio/transcriptions` |

Vérification en lecture seule : `outils/communs/llm_central_sante.sh --essai`.

## 2. Quel type de fournisseur choisir

[Source] Dans RAGFlow v1.0.0, `OpenAI-API-Compatible` (`conf/models/openai-api-compatible.json`) déclare les routes `chat/completions`, `embeddings`, `rerank`, `audio/transcriptions` et `audio/speech` : il couvre les quatre usages avec une clé. `VLLM` (`conf/models/vllm.json`) déclare chat, embedding et rerank mais pas de transcription ; son code est le même que celui d'`OpenAI-API-Compatible` (le second embarque le premier). Il n'existe aucun type « LiteLLM » dans RAGFlow. Choix : `OpenAI-API-Compatible` pour tout, une seule instance `llm-central`. `VLLM` n'apporte rien de plus pour le rerank, la route est la même (`/rerank`, format Jina/Cohere, que LiteLLM expose).

## 3. Pas à pas dans l'interface

**Étape 1. Ajouter le fournisseur** [À tester]
*Où* : menu du compte › « Fournisseurs de modèles » › `OpenAI-API-Compatible` › ajouter une instance.
Nom `llm-central` ; adresse `http://llm-central:8080/v1` ; clé : celle de `.env`. Ajouter quatre modèles, avec le nom exact et le type :

| Nom | Type | Contexte (jetons) |
|---|---|---|
| `chat` | Chat | 16 384 |
| `embed` | Embedding | 8 192 |
| `rerank` | Rerank | 8 192 |
| `transcribe` | Speech2text (transcription) | sans objet |

Si « Lister les modèles » propose aussi `gemma-4-e4b`, `qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3` et `faster-whisper-small` (alias bruts du service), ne retenir que les quatre noms fixes : les alias peuvent changer.

**Étape 2. Changer les modèles par défaut du compte**
*Où* : menu du compte › « Fournisseurs de modèles » › « Définir les modèles par défaut » (ou « Paramètres des modèles »).
Chat : `chat` ; Embedding : `embed` ; Rerank : `rerank` (facultatif ; sans rerank, RAGFlow classe par similarité seule) ; Transcription : `transcribe`.

**Étape 3. Réindexer les bases de connaissances**
L'embedding passe de bge-m3 bf16 (vLLM) à bge-m3 Q8_0 GGUF : les vecteurs sont proches mais pas identiques, et mélanger anciens et nouveaux dans un même index dégrade la recherche. Pour chaque base : « Configuration » › modèle d'embedding `embed` › enregistrer, puis relancer l'analyse de tous les documents (si l'interface refuse de changer le modèle d'une base déjà analysée, supprimer les passages ou recréer la base et ré-analyser). Contrôle : les nombres de passages doivent redevenir ceux d'avant.

**Étape 4. Régler les assistants, agents et synthèses**
Les assistants, agents et synthèses déjà créés gardent l'ancien nom de modèle (`gemma4:e4b`) : rouvrir chacun et choisir `chat @ llm-central`. Même chose pour le reranker des assistants.

**Étape 5. Contrôle**
Poser une question à un assistant : la réponse doit venir sans erreur et citer ses sources ; dans la console du service, la requête apparaît. Transcription : analyser `corpus/documents/message-vocal-production.mp3`.

## 4. Réflexion de `chat`

`chat` raisonne par défaut : le raisonnement (champ `reasoning_content`) est produit avant la réponse et compte dans le plafond de jetons. Mesuré [Vérifié] sur « Dis bonjour en un mot. » : `max_tokens` 300 sans coupure de la réflexion donne une réponse vide (le plafond est atteint dans le raisonnement) ; avec 1 500 jetons, réponse « Bonjour » en 3,7 s et 238 jetons ; avec `"chat_template_kwargs": {"enable_thinking": false}`, réponse en 0,18 s et 2 jetons.

[Source] RAGFlow n'a pas de champ de paramètres supplémentaires dans l'instance. Son pilote `VLLM`/`OpenAI-API-Compatible` ne fabrique `chat_template_kwargs.enable_thinking` que si le nom du modèle contient « qwen3 » ; le nom `chat` ne le contient pas, donc RAGFlow n'envoie rien et la réflexion reste active. Pour les assistants, l'option de raisonnement (`reasoning`) du chat, si l'interface l'expose, envoie `thinking: {type: enabled|disabled}` : l'effet via LiteLLM n'est pas vérifié [À tester]. Impact à prévoir : latence plus longue et consommation de jetons ; garder une marge de plafond de réponse (les 16 384 jetons couvrent prompt et réponse). Couper la réflexion pour tout le monde relève de LLM-Service, hors de ce dépôt.

## 5. Ancienne pile

`outils/communs/llm_service.sh` et `llm_service_vllm.sh` (et `outils/ragflow/reranker*.sh`) démarraient les conteneurs de l'ancien service : ils sont historiques, ne pas les lancer. Les résultats de `outils/resultats/` (avec `gemma4:e4b` sur vLLM) sont des preuves historiques, non comparables telles quelles aux mesures futures avec `chat`.
