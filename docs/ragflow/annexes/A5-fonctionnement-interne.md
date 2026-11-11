# A5. Fonctionnement interne

> **Objet** : architecture de RAGFlow 1.0, services, ports, installation du banc (fichier d'override), notions techniques (RAG, embeddings, découpage, recherche hybride).
> **Prérequis** : partie 1 du [manuel](../README.md), chapitres 01 à 04.
> **Version décrite** : RAGFlow v1.0.0 (image `infiniflow/ragflow:v1.0.0`), Windows 11 + WSL2 (Ubuntu 24.04), LLM-Service branche `service-vllm` (vLLM 0.29.0 : `gemma4:e4b`, `bge-m3`), contexte déclaré de 16 384 jetons.
> **Statut des informations** : [Vérifié] observé ou mesuré les 9 et 11 novembre 2026 sur la machine d'essai (Ryzen 5 9600X, 32 Go, RTX 4060 Ti 16 Go) ; [Source] documentation officielle ou code source au tag v1.0.0 ; [Estimation] calcul non mesuré ; [À tester] non documenté et non essayé.
> **Précautions** : annexe en cours de réécriture ; son contenu se trouve pour l'instant dans les documents cités ci-dessous.

## Sommaire

1. [Contenu actuel](#1-contenu-actuel)
2. [Dépannage](#dépannage)
3. [Sources](#sources)

## 1. Contenu actuel

Annexe en cours de réécriture. En attendant, le contenu se trouve dans : [Notions fondamentales](../00-notions-fondamentales.md), [Installation](../01-installation.md) (sections 2 à 5).

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| Information cherchée absente de cette page | annexe en cours de réécriture | lire les documents cités en section 1 |

## Sources

- Documents cités en section 1 ; résultats bruts dans `outils/resultats/ragflow/`.
