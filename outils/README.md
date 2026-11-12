# Outils du banc RAGFlow

Chaque affirmation des manuels renvoie à un script de ce dossier et à un résultat brut de `outils/resultats/`. Principe : le script produit un résultat brut (journal, JSON, capture), le résultat est committé tel quel, puis le manuel est rédigé à partir de ce seul résultat. Rien n'est écrit de mémoire.

## Outils communs (repris du banc Open Notebook, partagés par la série)

| Fichier | Rôle |
|---|---|
| `communs/diagnostic.sh` | diagnostic de la machine (WSL, CPU, RAM, GPU, Docker, `vm.max_map_count`, LLM-Service, accès réseau) |
| `communs/llm_central_sante.sh` | vérification en lecture seule du service LLM central (`/v1/models`, `--essai` : chat, embed, rerank, transcribe) ; clé lue dans `.env` |
| `communs/llm_service.sh` | HISTORIQUE : démarrait LLM-Service en branche `service-ollama` (CPU) ; ne plus lancer |
| `communs/llm_service_vllm.sh` | HISTORIQUE : démarrait LLM-Service en branche `service-vllm` (GPU) ; ne plus lancer |
| `communs/voix.sh` | HISTORIQUE : serveur de voix `rag-speaches` ; la transcription passe par `transcribe` du service LLM central ; ne plus lancer |
| `communs/versions.py` | dernière version stable de chaque composant, écarts justifiés |
| `communs/identite_github.py` | identité du projet sur GitHub (étoiles, licence, activité) |
| `communs/inventaire_modeles.py` | modèles déjà présents sur la machine, avant tout téléchargement |
| `communs/mesure_modeles.py` | mesures du service de modèles |
| `communs/generer_corpus.py`, `communs/generer_audio.py` | génération du corpus fictif (graine fixe) |
| `communs/banc/commun.py` | banc commun : interface d'adaptateur, notation, mesures, sorties JSON et Markdown |
| `communs/banc/tableau.py` | tableau comparatif des bancs d'une ou plusieurs solutions |
| `communs/banc/renoter.py` | renotation d'un banc sans rejouer les questions |
| `communs/captures/lancer.sh` | exécution d'un script de captures Playwright dans le conteneur officiel |
| `communs/verifier_docs.py` | vérification des manuels (liens, ancres, en-têtes, ton) ; 0 point exigé avant chaque commit |
| `communs/nettoyer.sh` | suppression complète d'une solution (`rag-<solution>`), jamais lancée automatiquement |
| `communs/nouvelle_solution.sh` | préparation du dépôt d'une solution suivante |

## Outils RAGFlow

| Fichier | Rôle |
|---|---|
| `ragflow/compose.override.yml` | écarts au compose officiel : ports sur `127.0.0.1`, conteneurs `rag-ragflow-*`, images figées, données dans `donnees/ragflow/`, réseaux `llm-net` et `rag-local` |
| `ragflow/installer.sh` | installation rejouable : sources au tag `v1.0.0`, réglages et secrets générés, démarrage, attente de l'état sain |
| `ragflow/configurer.py` | compte local, clé d'API, instance `llm-central` du fournisseur `OpenAI-API-Compatible` (chat, embed, rerank, transcribe) et modèles par défaut, interface en français |
| `ragflow/compose.sh` | appel de `docker compose` avec les fichiers et réglages du banc |
| `ragflow/demarrer.sh`, `ragflow/arreter.sh`, `ragflow/etat.sh` | démarrage, arrêt (données conservées), état |
| `ragflow/ressources.sh` | RAM par service, VRAM, taille des images, disque des données |
| `ragflow/verif_minimale.py` | vérification fonctionnelle minimale : import, question, citation |
| `ragflow/client.py` | fonctions partagées et contournements du SDK 1.0.0 |
| `ragflow/contexte.py` | réglage du contexte déclaré du modèle de chat |
| `ragflow/essai_contexte.py` | dépassement volontaire du contexte |
| `ragflow/banc.py` | adaptateur du banc commun ; `--reranker` reclasse les passages avec `rerank@llm-central@OpenAI-API-Compatible` |
| `ragflow/serie_banc.sh` | variantes du banc en série (contexte serré, agentique, hybride, gabarits) |
| `ragflow/captures/captures.py` | captures d'écran des manuels |
| `ragflow/captures/llm_central.py` | captures du branchement sur le service LLM central (chapitre 03) et du choix du reranker d'un assistant (chapitre 08) |
| `ragflow/demo.py`, `ragflow/essai_agent.py`, `ragflow/essai_compilation.py` | jeu de démonstration : base et assistant « Démo Vélanor », « Agent démo Vélanor », carte mentale « Essai-KC-mind_map-0816 » |

## Résultats

| Dossier | Contenu |
|---|---|
| `resultats/machine/` | diagnostics de la machine |
| `resultats/socle/` | mesures du service de modèles (reprises) |
| `resultats/open-notebook/` | bancs d'Open Notebook (repris pour le comparatif) |
| `resultats/ragflow/` | journaux d'installation et d'essai, bancs, versions, relecture, mesures de ressources |
