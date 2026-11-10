# 09. Sources externes

> **Objet** : alimenter une base de connaissances depuis un site web par son sitemap, et connaître la protection qui bloque les adresses privées.
> **Prérequis** : [datasets et découpage](03-datasets-et-decoupage.md).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré le 9 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : site de test fictif servi localement (conteneur `rag-site-test`, pages de `outils/ragflow/site-test/`), supprimé après l'essai ; connecteurs qui exigent un compte en ligne hors périmètre.

**Risque — réglage `ALLOW_ANY_HOST`.** Pour ingérer un site interne, il faut autoriser les adresses privées (`ALLOW_ANY_HOST=1`). Ce réglage vaut pour tout le serveur : les agents et leurs outils web peuvent alors joindre les machines du réseau local (attaque dite SSRF). Il n'a été activé que le temps d'un essai, puis remis à 0. [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-sitemap-autorise.log`) [Source] (`internal/common/allow_private_host.go`)

## Sommaire

1. [Connecteurs et synchronisation](#1-connecteurs-et-synchronisation)
2. [Sitemap d'un site local : refus par défaut](#2-sitemap-dun-site-local--refus-par-défaut)
3. [Sitemap avec adresses privées autorisées](#3-sitemap-avec-adresses-privées-autorisées)
4. [Dépannage](#dépannage)
5. [Sources](#sources)

## 1. Connecteurs et synchronisation

### Essentiel

Une source de données (connecteur) se déclare dans le menu du compte, « Sources de données », puis se lie à une base par « Lier une source de données » dans sa « Configuration ». La liaison déclenche une première synchronisation ; ensuite, la source est relue selon sa fréquence (`refresh_freq`, en minutes). [Vérifié] (libellés relevés par `captures.py` ; `essai_sitemap.py`)

Par l'API [Testée] :

| Étape | Appel |
|---|---|
| Créer le connecteur | `POST /api/v1/connectors` avec `{"name", "source": "sitemap", "config": {"sitemap_url": …}, "refresh_freq": 30}` |
| Le tester | `POST /api/v1/connectors/{id}/test` |
| Le lier à une base | `PUT /api/v1/datasets/{base}` avec `{"connectors": [{"id": …, "auto_parse": "1"}]}` |
| Suivre la synchronisation | `GET /api/v1/connectors/{id}/logs` |

### Pour aller plus loin

`POST /api/v1/connectors/{id}/rebuild` relance une synchronisation complète en supprimant d'abord les documents liés. [Source] (`internal/service/connector.go`) Non essayé : [À tester].

## 2. Sitemap d'un site local : refus par défaut

### Essentiel

Le site de test répond bien depuis le conteneur RAGFlow (HTTP 200 sur `http://rag-site-test/sitemap.xml`), mais le test du connecteur est refusé :

```text
{"code": 102, "message": "URL resolves to a non-public address (172.25.0.4), which is not allowed"}
```

La synchronisation échoue de même après trois tentatives, et la base reste vide. [Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-sitemap-refus.log`)

### Pour aller plus loin

RAGFlow résout le nom d'hôte et refuse toute adresse non publique : boucle locale (`127.0.0.1`), réseaux privés (dont les réseaux Docker en `172.x`), adresses de lien local. Un site de l'intranet est donc refusé comme un site sur la même machine. [Source] (`internal/common/http.go`, `AssertURLSafe`)

## 3. Sitemap avec adresses privées autorisées

### Essentiel

Avec `ALLOW_ANY_HOST=1` dans `donnees/ragflow/ragflow.env` puis redémarrage du serveur [Testée] :

| Mesure | Résultat |
|---|---|
| Test du connecteur | `{"code": 0, "message": "success"}` |
| Documents après synchronisation | `rag-site-test_index.html.md`, `rag-site-test_salon-2026.html.md` |
| Passages | 2 par page |
| Journal de synchronisation | `total_docs_indexed` 2, `error_msg` vide |

[Vérifié] (`outils/resultats/ragflow/essai-2026-11-09-sitemap-autorise.log`, script `outils/ragflow/essai_sitemap_autorise.sh`)

### Pour aller plus loin

Chaque page est convertie en Markdown avant analyse (suffixe `.html.md`). Le script remet `ALLOW_ANY_HOST` à 0 et redémarre le serveur à la fin de l'essai ; la valeur relue ensuite dans le conteneur est 0. [Vérifié] (même journal)

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| « URL resolves to a non-public address (…), which is not allowed » | garde contre les adresses privées | site public, ou `ALLOW_ANY_HOST=1` en connaissant le risque |
| Base vide après liaison d'une source | synchronisation en échec | `GET /api/v1/connectors/{id}/logs`, champ `error_msg` |
| Documents supprimés après une resynchronisation complète | `rebuild` vide d'abord la base liée | préférer la synchronisation périodique |

## Sources

- Scripts : `outils/ragflow/essai_sitemap.py`, `outils/ragflow/essai_sitemap_autorise.sh`, site `outils/ragflow/site-test/`
- Journaux : [refus](../../outils/resultats/ragflow/essai-2026-11-09-sitemap-refus.log), [autorisé](../../outils/resultats/ragflow/essai-2026-11-09-sitemap-autorise.log)
- Code au tag v1.0.0 : `internal/syncer/connector/sitemap.go`, `internal/common/http.go`, `docs/guides/.../data_source_configuration.md` ; https://ragflow.io/docs/
