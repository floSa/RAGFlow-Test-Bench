# Relecture avant installation — RAGFlow v1.0.0

Relu le 9 novembre 2026, sources au tag `v1.0.0` (commit `db1cd5929a7885a3074547791f5ecc4d2f891739`), clonées dans `sources/ragflow/` (ignoré par git). Lecture directe de `docker/docker-compose.yml`, `docker/docker-compose-base.yml`, `docker/.env`, `docker/service_conf.yaml.template`, `docker/kvrocks-entrypoint.sh` ; lecture du code Go, du `Dockerfile`, de `docs/` et du SDK confiée à un sous-agent (synthèse ci-dessous, avec chemins dans le dépôt cloné).

## Architecture au tag v1.0.0

- RAGFlow 1.0 est une réécriture en Go (`docs/release_notes.md`) : le backend Python et `launch_backend_service.sh` ne sont plus lancés par `entrypoint.sh`. Une file NATS remplace Redis pour les tâches ; Kvrocks sert de cache.
- Profils par défaut : `elasticsearch`, `cpu`, `metadata-mysql`. Services lancés : `ragflow-cpu` (serveur, interface nginx, administration, ingestion), `es01` (Elasticsearch 8.11.3), `mysql` (8.0.40), `minio` (`pgsty/silo`, fork de MinIO), `kvrocks` (2.16.0), `nats` (2.14.2).
- Le profil `tei-cpu`/`tei-gpu` lance un serveur d'embedding TEI (Qwen3-Embedding-0.6B) : inutile ici, l'embedding vient de `vllm-embed` (LLM-Service). Aucun reranker n'est embarqué (`internal/entity/models/builtin.go`).
- Les modèles DeepDoc (mise en page, OCR, structure des tableaux, au format ONNX) sont embarqués dans l'image (`Dockerfile`, lignes 25 à 50) et tournent sur CPU. Aucun téléchargement au démarrage relevé dans `entrypoint.sh`.

## Points relevés

| N° | Point | Risque | Traitement dans le banc |
|---|---|---|---|
| 1 | Tous les ports publiés sans adresse, donc sur `0.0.0.0` : 80, 443, 9380, 9381 (RAGFlow), 1200 (Elasticsearch), 3306 (MySQL), 9000 et 9001 (MinIO), 6379 (Kvrocks), 4222 et 8222 (NATS, sans authentification visible) | exposition réseau | override : 8088 (web), 9380 (API) et 9381 (administration) sur `127.0.0.1` ; tous les autres retirés |
| 2 | Mots de passe par défaut `infini_rag_flow` pour Elasticsearch, MySQL, MinIO, Kvrocks ; `admin` pour l'administrateur | accès trivial si un port fuit | secrets aléatoires générés dans `donnees/ragflow/ragflow.env` (droits 600) |
| 3 | `--init-superuser` crée `admin@ragflow.io` / `ADMIN_DEFAULT_PASSWORD` au premier démarrage ; ce compte reçoit un refus 403 sur `/api/v1` (`internal/handler/auth.go`) | compte d'administration prévisible | mot de passe généré ; travail fait avec un compte local fictif inscrit normalement |
| 4 | `ALLOW_ANY_HOST=0` par défaut ; à 1, ouvre des requêtes vers les hôtes privés (`internal/agent/tool/ssrf.go`) | SSRF | laissé à 0 |
| 5 | Profil `sandbox` : image `latest`, `privileged: true`, socket Docker monté | prise de contrôle de l'hôte | profil non activé (et non pris en charge en local selon les notes de version) |
| 6 | `kvrocks` tourne en `root` (`user: "0:0"`) pour écrire sa configuration | faible (réseau interne seulement) | gardé tel quel, port non publié |
| 7 | `MEM_LIMIT` (8 Go par défaut) ne s'applique qu'au moteur documentaire | RAM | ramené à 4 Gio (Elasticsearch prend environ la moitié en tas Java) |
| 8 | `service_conf.yaml.template` : section `user_default_llm` sans effet dans l'édition communautaire (`internal/server/config/stub.go`) | modèles non déclarés automatiquement | déclaration par l'API HTTP (`outils/ragflow/configurer.py`) |
| 9 | SDK `ragflow-sdk` 1.0.0 : exige Python 3.13 (`sdk/python/pyproject.toml`) ; `Session.ask` appelle `/chats/{id}/completions`, alias retiré en 1.0 selon `docs/references/http_api_reference.md` | bogue probable du SDK | à vérifier à l'essai ; contournement par `POST /api/v1/chat/completions` |
| 10 | Notes de version : la montée depuis 0.27.x migre la base de façon irréversible | perte de retour arrière | installation neuve ; à signaler dans le manuel Exploitation |
| 11 | `HF_ENDPOINT` fixé à `hf-mirror.com` dans l'image (`Dockerfile`, ligne 293), sans usage au démarrage relevé | téléchargement par un miroir tiers | surveillé dans les journaux pendant les essais |
| 12 | Sitemap : adresses privées et `127.0.0.1` refusées (`docs/.../data_source_configuration.md`) | essai d'un site local de test impossible en l'état | à vérifier ; sinon [À tester] |

## Branchement des modèles

- Fournisseurs disponibles : `VLLM`, `OpenAI-API-Compatible` (même pilote que VLLM), `Ollama` (`conf/llm_factories.json`).
- RAGFlow n'envoie jamais `num_ctx` (pilote Ollama) ; il envoie `max_tokens` ramené à « contexte déclaré − jetons du prompt » (`internal/service/chat_pipeline.go`). Le contexte d'un modèle est le `max_tokens` déclaré à son ajout (8 192 par défaut si 0).
- Choix du banc : fournisseur `VLLM`, `http://vllm-central:8000/v1` (chat, `gemma4:e4b`) et `http://vllm-embed:8000/v1` (embedding, `bge-m3`). Contexte déclaré pour le chat : 16 384 jetons (taille commune de la série), alors que vLLM accepte 32 768.
- Déclaration : `PUT /api/v1/providers`, `POST /api/v1/providers/VLLM/instances`, puis `PATCH /api/v1/models/default` par type de modèle.
