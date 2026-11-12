# A7. Bascule vers le service LLM central

> **Objet** : brancher RAGFlow sur le service LLM central (LLM-Service, LiteLLM) à la place de l'ancienne pile `vllm-central` / `vllm-embed` / `rag-speaches`, depuis l'interface web.
> **Prérequis** : le service tourne (géré à part, jamais démarré par ce dépôt) ; la clé du service est dans `.env` (`LLM_CENTRAL_KEY`) ; RAGFlow joint le réseau `llm-net`.
> **Version décrite** : RAGFlow v1.0.0, service LLM central (LiteLLM v1.109.0, llama-swap v272, llama.cpp build 12282, Speaches 0.8.3), essais des 11 et 12 novembre 2026.
> **Statut des informations** : [Vérifié] requêtes réelles du 11 novembre 2026 depuis `rag-ragflow-server` et l'hôte (journal : `outils/resultats/ragflow/essai-llm-central-2026-11-11.log`) ; [Source] code de RAGFlow v1.0.0 (`sources/ragflow/conf/models/`, `internal/entity/models/`) ; [Vérifié] le 12 novembre 2026 : script de configuration, déclaration à la souris, défauts, recréation du jeu de démonstration (`outils/resultats/ragflow/configuration-2026-11-12.log`, `bascule-llm-central-2026-11-12.log`, `captures/llm-central/`, `demo-2026-11-12.log`) ; [À tester] l'effet de l'option « Thinking » des assistants à travers LiteLLM, le changement du modèle d'embedding d'une base déjà analysée ; [Estimation] aucune.
> **Précautions** : ne rien démarrer ni arrêter côté LLM-Service ; la clé reste dans `.env`, jamais dans un fichier suivi ; réindexer modifie les bases : sauvegarder avant (annexe [A4](A4-exploitation.md)).

## Sommaire

1. Le service ; 2. Quel type de fournisseur choisir ; 3. Pas à pas ; 4. Réflexion de `chat` ; 5. Ancienne pile ; Dépannage ; Sources.

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

## 3. Pas à pas

La déclaration se fait par le script (`uv run python outils/ragflow/configurer.py`, chapitre [02](../manuel/02-installer-ragflow.md), étape 7) ou à la souris (chapitre [03](../manuel/03-premiers-pas.md), étapes 7 à 19, avec captures). Les deux chemins ont été exécutés le 12 novembre 2026 et donnent le même résultat. [Vérifié]

| Étape | Ce qui a été fait | Résultat | Preuve |
|---|---|---|---|
| 1. Instance | `OpenAI-API-Compatible` › « Add instance » : `llm-central`, clé, `http://llm-central:8080/v1`, « Lister les modèles » | 9 modèles listés avec le bon type (« LLM », « Embedding », « Rerank », « ASR ») ; 5 alias retirés (`bge-m3`, `bge-reranker-v2-m3`, `faster-whisper-small`, `gemma-4-e4b`, `qwen3.5-4b`), 4 noms fixes gardés | `outils/resultats/ragflow/captures/llm-central/modeles-instance.log` |
| 2. Taille de contexte | « Modifier le modèle » : `chat` 16 384, `embed` et `rerank` 8 192 | « Lister les modèles » laisse 0 aux noms fixes ; valeurs relues après rechargement | `captures/llm-central/modeles-reglages.log` |
| 3. Défauts du compte | « Définir les modèles par défaut » : chat `chat`, embedding `embed`, Speech2txt `transcribe`, rerank `rerank` | message « Modifié » à chaque choix ; `GET /api/v1/models/default` confirme | idem, `bascule-llm-central-2026-11-12.log` |
| 4. Anciennes instances | `VLLM` : `llm-service-chat`, `llm-service-embed` puis le fournisseur, par l'API ; `voix-locale` à la souris | fournisseur `OpenAI-API-Compatible` seul, instance `llm-central` seule | `bascule-llm-central-2026-11-12.log` |
| 5. Bases | « Démo Vélanor » recréée par `demo.py` (9 documents, 26 passages, 55 s), carte mentale recréée sous « Essai-KC-mind_map-0816 » ; anciennes bases supprimées | réponses citées justes | `demo-2026-11-12.log`, `essai-2026-11-12-compilation-mind_map.log` |
| 6. Agent | « Agent démo Vélanor » recréé par `essai_agent.py` avec `chat@llm-central@OpenAI-API-Compatible` | réponses justes en 17 à 26 s, raisonnement visible entre balises `<think>` | `essai-2026-11-12-agent.log` |

Piège : une base retient l'identifiant interne du modèle d'embedding (`tenant_embd_id`). L'ordre retenu est donc : instance et défauts d'abord, bases ensuite. Changer le modèle d'embedding d'une base déjà analysée n'a pas été essayé : la base a été recréée. [Vérifié] (`installation-2026-11-12-verif.log` : `embedding=` donne un identifiant)

## 4. Réflexion de `chat`

`chat` raisonne par défaut : le raisonnement (champ `reasoning_content`) est produit avant la réponse et compte dans le plafond de jetons. Mesuré [Vérifié] sur « Dis bonjour en un mot. » : `max_tokens` 300 sans coupure de la réflexion donne une réponse vide (le plafond est atteint dans le raisonnement) ; avec 1 500 jetons, réponse « Bonjour » en 3,7 s et 238 jetons ; avec `"chat_template_kwargs": {"enable_thinking": false}`, réponse en 0,18 s et 2 jetons.

[Source] RAGFlow n'a pas de champ de paramètres supplémentaires dans l'instance. Son pilote `VLLM`/`OpenAI-API-Compatible` ne fabrique `chat_template_kwargs.enable_thinking` que si le nom du modèle contient « qwen3 » ; le nom `chat` ne le contient pas, donc RAGFlow n'envoie rien et la réflexion reste active. Pour les assistants, l'option de raisonnement (« Thinking » du panneau, chapitre 08), envoie `thinking: {type: enabled|disabled}` : l'effet via LiteLLM n'est pas vérifié [À tester]. Constat sur l'agent : le raisonnement apparaît dans la réponse, entre balises `<think>` ; les assistants ne l'affichent pas. [Vérifié] (`essai-2026-11-12-agent.log`, `demo-2026-11-12.log`) Impact à prévoir : latence plus longue et consommation de jetons ; garder une marge de plafond de réponse (les 16 384 jetons couvrent prompt et réponse). Couper la réflexion pour tout le monde relève de LLM-Service, hors de ce dépôt.

## 5. Ancienne pile

`outils/communs/llm_service.sh`, `llm_service_vllm.sh`, `voix.sh` (et `outils/ragflow/reranker*.sh`) démarraient les conteneurs de l'ancien service : ils sont historiques, ne pas les lancer. Le conteneur `rag-speaches` tourne encore sur la machine d'essai mais n'est plus branché. Les résultats de `outils/resultats/` (avec `gemma4:e4b` sur vLLM) sont des preuves historiques, non comparables telles quelles aux mesures futures avec `chat`.

## Dépannage

| Symptôme | Cause probable | Remède |
|---|---|---|
| « Lister les modèles » échoue ou erreur 401 | clé absente ou fausse | recopier `LLM_CENTRAL_KEY` du `.env` ; tester avec `outils/communs/llm_central_sante.sh` |
| Adresse injoignable depuis RAGFlow | `127.0.0.1` désigne le conteneur | utiliser `http://llm-central:8080/v1` (réseau `llm-net`) |
| Réponse vide ou coupée | plafond atteint pendant la réflexion | augmenter la longueur de réponse autorisée ; voir section 4 |
| Scores de rerank négatifs | scores bruts non bornés | normal : seul l'ordre compte |

## Sources

- `sources/ragflow/conf/models/openai-api-compatible.json`, `vllm.json` ; `sources/ragflow/internal/entity/models/vllm.go`, `openai_api_compatible.go`.
- `outils/resultats/ragflow/essai-llm-central-2026-11-11.log`.
