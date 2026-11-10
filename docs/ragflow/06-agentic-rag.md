# 06. Agentic RAG

> **Objet** : comparer la réponse directe (« Naive ») et le mode agentique (« Agentic ») : qualité, citations, latence.
> **Prérequis** : [assistants de chat et citations](05-assistants-et-citations.md).
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré le 9 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : assistant d'essai « Banc-agentic » ; corpus fictif.

## Sommaire

1. [Les deux modes](#1-les-deux-modes)
2. [Résultats du banc](#2-résultats-du-banc)
3. [Ce qui se passe quand l'agent échoue](#3-ce-qui-se-passe-quand-lagent-échoue)
4. [Dépannage](#dépannage)
5. [Sources](#sources)

## 1. Les deux modes

### Essentiel

Sous la zone de saisie d'une discussion, un sélecteur propose « Naive » (par défaut : recherche puis réponse en une passe) et « Agentic » (« Self-directed corpus exploration » : le modèle décide lui-même des recherches à lancer, en plusieurs tours).

![Modes de réponse](img/06-agentic-rag/01-modes-de-reponse.png)

Par l'API, le mode agentique se demande en ajoutant `"reasoning": 5` au corps de `POST /api/v1/chat/completions` [Testée] (`outils/ragflow/banc.py`, option `--agentic`).

### Pour aller plus loin

Le mode agentique remplace les « niveaux de réflexion » des versions 0.x. Son déroulé suit un gabarit d'agent, `smart-reasoning` par défaut (`conf/agentic_rag.yaml`), surchargeable par `prompt_config.agentic_rag`. [Source] (`internal/service/chat_pipeline.go`, `docs/release_notes.md`)

## 2. Résultats du banc

### Essentiel

Même base, même assistant, mêmes 38 questions [Vérifié] :

| Mode | Exactes (34) | Refus corrects (4) | Bon document cité | Réponses sans citation | Médiane | p95 |
|---|---|---|---|---|---|---|
| Naive (défaut) | 33 | 4 | 34 | 0 | 1,28 s | 1,88 s |
| Agentic | 30 | 4 | 29 | 5 | 4,52 s | 7,22 s |

(`outils/resultats/ragflow/banc-2026-11-09-defaut.json`, `outils/resultats/ragflow/banc-2026-11-09-agentic.json`)

Sur ce corpus et avec ce petit modèle, le mode agentique est moins juste et 3,5 fois plus lent. La réponse directe reste le bon choix.

### Pour aller plus loin

Le mode agentique gagne pourtant sur les questions multi-documents (3 sur 3, contre 2 sur 3) : il trouve seul le délai contractuel de Batterix dans le contrat scanné (Q30). Il perd quatre questions simples (Q06, Q07, Q26, Q27). [Vérifié] (même fichier, `par_type`)

## 3. Ce qui se passe quand l'agent échoue

### Essentiel

Dans les échecs, le modèle ne lance pas de recherche et répond comme s'il n'avait accès à aucun document, par exemple pour Q26 : « Je n'ai pas accès à une base de données contenant les numéros de téléphone des services après-vente… ». La réponse est alors donnée sans citation. [Vérifié] (`banc-2026-11-09-agentic.json`, Q06, Q07, Q26, Q27)

### Pour aller plus loin

Par l'API, toutes les réponses agentiques commencent par un bloc `<think>…</think>`, qui répète ou prépare la réponse (38 réponses sur 38) ; un programme qui affiche la réponse doit retirer ce bloc. Un modèle plus grand, plus habitué à l'appel d'outils, suivrait sans doute mieux le déroulé agentique [Estimation] ; non essayé, le socle ne servant qu'un modèle de réponse.

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Réponse agentique « je n'ai pas accès à… » sans citation | le modèle n'a pas lancé de recherche | repasser en « Naive », ou reposer la question |
| Bloc `<think>…</think>` dans la réponse de l'API | sortie du mode agentique | retirer le bloc avant affichage |
| Réponse 3 à 4 fois plus lente | plusieurs tours de recherche et de génération | normal en mode agentique |

## Sources

- Bancs : [Naive](../../outils/resultats/ragflow/banc-2026-11-09-defaut.md), [Agentic](../../outils/resultats/ragflow/banc-2026-11-09-agentic.md)
- Script : `outils/ragflow/banc.py` (`--agentic`), capture `outils/ragflow/captures/captures.py` (scénario `agentique`)
- Code au tag v1.0.0 : `internal/service/chat_pipeline.go`, `conf/agentic_rag.yaml` ; https://ragflow.io/docs/
