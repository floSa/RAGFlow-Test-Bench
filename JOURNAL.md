# Journal de la mission RAGFlow

Mission : `kit/PROMPT.md` pour la fiche `kit/fiches/02-ragflow.md` (kit distribué à part dans `kit-manuels-rag-local.zip`, hors dépôt).
Une entrée par étape : date et heure, phase, ce qui a été fait, résultat, fichiers touchés, prochaine étape.

## Décisions en attente

Aucune pour l'instant.

## Écarts au kit, décidés au lancement

- **Pas de `git push`** : interdit par le bloc « Lancement » de la fiche, qui prime sur la règle globale de l'utilisateur. Aucun dépôt distant n'est configuré.
- **Machine de profil B** (Ryzen 5 9600X, RTX 4060 Ti 16 Go, 32 Go de RAM dans WSL) : LLM-Service tourne en branche `service-vllm` avec Gemma 4 E4B (chat) et bge-m3 (embedding), comme le dernier banc Open Notebook (`outils/resultats/open-notebook/banc-2026-11-09-gpu-vllm.json`). Ces modèles sont gardés pour que la comparaison tienne ; qwen3:4b-instruct et ministral-3:3b ne sont pas servis par vLLM ici. Le profil A est donné en [Estimation].
- **Chemins** : le kit cite `~/Projets/…` ; sur cette machine tout est sous `~/mes_projets/…` (LLM-Service : `~/mes_projets/Projet-IA/LLM-Service`).
- **Ports hors périmètre** : `vllm-central`, `vllm-embed` (LLM-Service) et `watch-speaches` publient sur `0.0.0.0` ; ils n'appartiennent pas à cette mission et ne sont pas modifiés. La vérification « ports sur 127.0.0.1 » porte sur les conteneurs `rag-ragflow-*`.
- **Consigne de l'utilisateur** : service de modèles extérieur à RAGFlow, modèles de taille équilibrée pour une application fluide (pas de gros modèle).

## Entrées

### 2026-11-09 17:25 — Mise en place du dépôt

- Fait : extraction du kit, `git init`, `.gitignore`, reprise du corpus (empreintes conformes, 9 documents, 38 questions), des outils communs (alignés sur la variante GPU du banc Open Notebook), des mesures du socle et des résultats Open Notebook (CPU et GPU).
- Résultat : dépôt propre, un commit par bloc.
- Fichiers : `.gitignore`, `corpus/`, `outils/communs/`, `outils/resultats/{socle,machine,open-notebook}/`.
- Prochaine étape : phase A, diagnostic de la machine.

### 2026-11-09 17:40 — Phases A et B : diagnostic et socle

- Fait : `outils/communs/diagnostic.sh` complété (vm.max_map_count, LLM-Service) puis lancé.
- Résultat (`outils/resultats/machine/diagnostic-2026-11-09.json`) : Ubuntu 24.04.5 dans WSL2, AMD Ryzen 5 9600X (12 fils), 32 096 Mo de RAM, 4 096 Mo de swap, 525 Go libres, RTX 4060 Ti 16 Go (pilote 616.92), GPU accessible dans un conteneur, Docker 29.9.3 (moteur installé dans Ubuntu, `/var/lib/docker`, pas Docker Desktop), Compose 5.7.0, `vm.max_map_count` = 1 048 576 (Elasticsearch satisfait sans `sysctl`), port `127.0.0.1` joignable depuis WSL (HTTP 200), registres et Hugging Face joignables.
- LLM-Service en marche, branche `service-vllm` : `vllm-central` (Gemma 4 E4B quantifié w4a16, contexte 32 768) et `vllm-embed` (bge-m3, 8 192), vLLM 0.29.0. Serveur de voix `rag-speaches` en marche.
- Incident : le test GPU du diagnostic tire l'image `ollama/ollama` figée par empreinte (environ 5,6 Go) ; compté dans le budget de téléchargement.
- Aucun bloquant. Socle repris tel quel (pas de nouvelle mesure du service de modèles : version et modèles inchangés depuis le banc GPU Open Notebook du 9 novembre).
- Prochaine étape : phase C, cadrage (versions, relecture du compose, plan des manuels).
