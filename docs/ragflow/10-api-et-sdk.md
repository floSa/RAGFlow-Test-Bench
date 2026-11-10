# 10. API HTTP et SDK Python

> **Objet** : automatiser RAGFlow : clé d'API, bases de connaissances, import, analyse, assistants et questions, par l'API HTTP et par le SDK `ragflow-sdk`.
> **Prérequis** : [installation](01-installation.md), [assistants de chat et citations](05-assistants-et-citations.md).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), `ragflow-sdk` 1.0.0 sous Python 3.13 (uv), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré le 9 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : la clé d'API donne tous les droits du compte : elle reste dans `donnees/` (ignoré par git) et n'est jamais affichée par les exemples ; objets d'exemple supprimés par `06_nettoyer_exemples.py`.

**Risque — défauts du SDK 1.0.0.** Deux appels du SDK ne fonctionnent pas comme attendu avec le serveur 1.0.0 : `Session.ask` sur un assistant de chat répond 404, et `DataSet.parse_documents` a une fois rendu la main avant la fin réelle de l'analyse. Les contournements sont donnés en section 4. [Vérifié] (`outils/resultats/ragflow/installation-2026-11-09-verif.log`, `outils/resultats/ragflow/installation-2026-11-09-verif-essai1.log`)

## Sommaire

1. [Clé d'API et environnement](#1-clé-dapi-et-environnement)
2. [Les appels utiles](#2-les-appels-utiles)
3. [Exemples exécutés](#3-exemples-exécutés)
4. [Défauts du SDK 1.0.0 et contournements](#4-défauts-du-sdk-100-et-contournements)
5. [Dépannage](#dépannage)
6. [Sources](#sources)

## 1. Clé d'API et environnement

### Essentiel

- Clé d'API : menu du compte, « API », ou `POST /api/v1/system/keys` avec `{"name": "…"}` une fois connecté [Testée] (`outils/ragflow/configurer.py`). Elle s'envoie dans l'en-tête `Authorization: Bearer <clé>`.
- Adresse de l'API : `http://127.0.0.1:9380` depuis WSL (l'interface sur 8088 la relaie aussi sous `/api/`).
- SDK : `ragflow-sdk` 1.0.0, même version que le serveur ; il exige Python 3.13. Dans ce dépôt [Testée] :

```bash
uv sync
uv run python exemples/ragflow/03_importer_et_analyser.py
```

### Pour aller plus loin

Le compte d'administration créé au premier démarrage reçoit un refus sur `/api/v1` : utiliser un compte ordinaire. [Source] (`internal/handler/auth.go`) Les routes d'administration sont sur le port 9381.

## 2. Les appels utiles

### Essentiel

| Besoin | API HTTP | SDK |
|---|---|---|
| Santé (sans clé) | `GET /api/v1/system/healthz` | — |
| Créer une base | `POST /api/v1/datasets` (`name`, `parser_id`) | `rag.create_dataset(name=…, parser_id="general")` |
| Téléverser | `POST /api/v1/datasets/{base}/documents` (multipart) | `ds.upload_documents([{"display_name", "blob"}])` |
| Lancer l'analyse | `POST /api/v1/datasets/{base}/chunks` (`document_ids`) | `ds.async_parse_documents(ids)` |
| Suivre l'analyse | `GET /api/v1/datasets/{base}/documents` (`progress`, `chunk_count`) | `ds.list_documents(id=…)` |
| Recherche seule | `POST /api/v1/retrieval` | `rag.retrieve(question=…, dataset_ids=[…])` |
| Créer un assistant | `POST /api/v1/chats` | `rag.create_chat(name=…, dataset_ids=[…])` |
| Poser une question | `POST /api/v1/chat/completions` (`chat_id`, `session_id`, `question`, `stream: false`) | (défaut, voir section 4) |
| Agents | `POST /api/v1/agents/chat/completions` | `agent.create_session()`, `session.ask(…)` |

[Testée] (scripts de `outils/ragflow/` et `exemples/ragflow/`)

### Pour aller plus loin

- Réponse d'une question : `data.answer` (texte avec marqueurs `[ID:n]`) et `data.reference.chunks` (tous les passages fournis au modèle, avec `document_name`, `content`, `positions`, `similarity`). Garder les seuls passages dont l'indice figure dans `[ID:n]` pour connaître les sources réellement citées ; voir le manuel [05](05-assistants-et-citations.md).
- Ruptures par rapport aux versions 0.x : `chunk_method="naive"` devient `parser_id="general"` ; plusieurs anciennes routes sont retirées, dont `/api/v1/chats/{id}/completions`. [Source] (`docs/references/http_api_reference.md`)

## 3. Exemples exécutés

### Essentiel

Six exemples courts dans `exemples/ragflow/`, lancés par `exemples/ragflow/lancer.sh`, qui écrit leur sortie réelle dans [`sorties_verifiees.txt`](../../exemples/ragflow/sorties_verifiees.txt) [Testée] :

| Exemple | Ce qu'il fait | Sortie obtenue (extrait) |
|---|---|---|
| `01_sante.sh` | santé et interface | `{"db":"ok",…,"status":"ok"}`, `interface web : HTTP 200` |
| `02_modeles_par_defaut.sh` | modèles par défaut du compte | `chat -> gemma4:e4b @ llm-service-chat ( VLLM )` |
| `03_importer_et_analyser.py` | base, import de `faq-sav.html`, analyse | `1 passage(s), 153 jetons` |
| `04_question_assistant.py` | assistant et question par l'API HTTP | `Le cadre est garanti pendant 7 ans [ID:0].` |
| `05_recherche_seule.py` | recherche sans génération | `similarité 0.407 \| faq-sav.html` |
| `06_nettoyer_exemples.py` | suppression des objets d'exemple | `supprimés : 1 assistant(s), 1 dataset(s)` |

[Vérifié] (`exemples/ragflow/sorties_verifiees.txt`)

### Pour aller plus loin

Les exemples se lancent depuis la racine du dépôt (ils lisent la clé dans `donnees/ragflow/compte.json`). Ils n'utilisent que le SDK et `requests`, déjà installé avec lui.

## 4. Défauts du SDK 1.0.0 et contournements

### Essentiel

| Défaut constaté | Effet | Contournement [Testée] |
|---|---|---|
| `Session.ask` d'un assistant de chat appelle `/api/v1/chats/{id}/completions`, route retirée du serveur 1.0 | `Exception: Not Found: /api/v1/chats/…/completions` | `POST /api/v1/chat/completions` avec `chat_id`, `session_id`, `question`, `stream: false` (`outils/ragflow/client.py`, `demander`) |
| `DataSet.parse_documents` a rendu « DONE » avec 0 passage (1 fois sur 3) | création d'un assistant refusée : « doesn't own parsed file » | attendre `progress` = 1 et `chunk_count` > 0 (`client.attendre_analyse`) |
| `Chat.vector_similarity_weight` garde la valeur par défaut 0,3 | réglage réel mal lu | lire `keywords_similarity_weight` (vecteurs = 1 − mots-clés) |

[Vérifié] (`outils/resultats/ragflow/installation-2026-11-09-verif.log`, `installation-2026-11-09-verif-essai1.log`, `essai-2026-11-09-sdk-defauts.log`)

### Pour aller plus loin

- `Session.ask` est un générateur, même avec `stream=False` : il rend un seul message, à lire par `next(iter(session.ask(…)))` ; `.content` directement donne « 'generator' object has no attribute 'content' ». Pour un **agent**, il fonctionne. [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-sdk-defauts.log`, `essai-2026-11-09-agent.log`)
- `RAGFlow.create_agent` renvoie `None` : retrouver l'agent par `list_agents()`. [Source] (`sdk/python/ragflow_sdk/ragflow.py`)
- Le texte d'un passage HTML colle des éléments voisins (« après-venteDocument fictif.Quelle ») : sans effet sur la réponse observée. [Vérifié] (`sorties_verifiees.txt`, exemple 03)

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `Not Found: /api/v1/chats/…/completions` | défaut du SDK 1.0.0 | API HTTP `POST /api/v1/chat/completions` |
| `the dataset … doesn't own parsed file` | analyse pas terminée | attendre `chunk_count` > 0 |
| `'generator' object has no attribute 'content'` | `Session.ask` est un générateur | `next(iter(session.ask(…)))` |
| `ragflow-sdk` refuse de s'installer | Python autre que 3.13 | `uv python install 3.13`, `uv sync` |
| Réponse HTTP en flux au lieu d'un JSON | `stream` absent du corps | `"stream": false` |

## Sources

- Exemples : `exemples/ragflow/`, [sorties vérifiées](../../exemples/ragflow/sorties_verifiees.txt)
- Scripts : `outils/ragflow/client.py`, `outils/ragflow/verif_minimale.py`, `outils/ragflow/banc.py`
- Référence de l'API au tag v1.0.0 : `docs/references/http_api_reference.md` ; SDK : `sdk/python/ragflow_sdk/` ; https://ragflow.io/docs/
