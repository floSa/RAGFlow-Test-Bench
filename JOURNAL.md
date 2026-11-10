# Journal de la mission RAGFlow

Mission : `kit/PROMPT.md` pour la fiche `kit/fiches/02-ragflow.md` (kit distribué à part dans `kit-manuels-rag-local.zip`, hors dépôt).
Une entrée par étape : date et heure, phase, ce qui a été fait, résultat, fichiers touchés, prochaine étape.

## Décisions en attente

1. **Montée de vLLM dans LLM-Service** : 0.29.0 en service, 0.32.0 est la dernière stable (`outils/resultats/ragflow/versions-2026-11-09.json`). Gardé tel quel : LLM-Service est partagé et la comparaison avec le banc GPU Open Notebook en dépend. Option prudente retenue : ne rien changer.
2. **Port de l'interface** : 8088 au lieu de 8080 (8080 occupé sur `127.0.0.1` par un processus Python de l'utilisateur, non touché).
3. **`git push`** : interdit par la fiche ; aucun dépôt distant. À créer et pousser à la main.
4. **Reranker** : aucun dans le socle ; en ajouter un à LLM-Service pour essayer le reranking ?
5. **Ports `0.0.0.0` hors mission** : `vllm-central`, `vllm-embed`, `watch-speaches` ; à traiter dans leurs dépôts.

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

### 2026-11-09 17:28 — Phases A et B : diagnostic et socle

- Fait : `outils/communs/diagnostic.sh` complété (vm.max_map_count, LLM-Service) puis lancé.
- Résultat (`outils/resultats/machine/diagnostic-2026-11-09.json`) : Ubuntu 24.04.5 dans WSL2, AMD Ryzen 5 9600X (12 fils), 32 096 Mo de RAM, 4 096 Mo de swap, 525 Go libres, RTX 4060 Ti 16 Go (pilote 616.92), GPU accessible dans un conteneur, Docker 29.9.3 (moteur installé dans Ubuntu, `/var/lib/docker`, pas Docker Desktop), Compose 5.7.0, `vm.max_map_count` = 1 048 576 (Elasticsearch satisfait sans `sysctl`), port `127.0.0.1` joignable depuis WSL (HTTP 200), registres et Hugging Face joignables.
- LLM-Service en marche, branche `service-vllm` : `vllm-central` (Gemma 4 E4B quantifié w4a16, contexte 32 768) et `vllm-embed` (bge-m3, 8 192), vLLM 0.29.0. Serveur de voix `rag-speaches` en marche.
- Incident : le test GPU du diagnostic tire l'image `ollama/ollama` figée par empreinte (environ 5,6 Go) ; compté dans le budget de téléchargement.
- Aucun bloquant. Socle repris tel quel (pas de nouvelle mesure du service de modèles : version et modèles inchangés depuis le banc GPU Open Notebook du 9 novembre).
- Prochaine étape : phase C, cadrage (versions, relecture du compose, plan des manuels).

### 2026-11-09 17:31 — Phase C : cadrage

- Fait : dernière version stable relevée (RAGFlow v1.0.0 du 6 novembre 2026, `ragflow-sdk` 1.0.0), sources clonées au tag dans `sources/ragflow/` (ignoré par git), relecture du compose et lecture du code par un sous-agent, plan des manuels.
- Résultat : `outils/resultats/ragflow/versions-2026-11-09.json`, `outils/resultats/ragflow/relecture.md`, `docs/ragflow/plan-des-manuels.md`. Points marquants : RAGFlow 1.0 réécrit en Go ; tous les ports du compose officiel sur `0.0.0.0` ; mots de passe par défaut ; modèles déclarés seulement par l'API (section `user_default_llm` sans effet) ; aucun reranker embarqué ; SDK sous Python 3.13.
- Prochaine étape : phase D.

### 2026-11-09 17:38 — Phase D : installation testée

- Fait : override compose, `installer.sh`, `configurer.py` (compte local, clé d'API, modèles VLLM et transcription), `verif_minimale.py`, `demarrer.sh`, `arreter.sh`, `etat.sh`, `ressources.sh`, `compose.sh`. Open Notebook arrêté avant (son `arreter.sh`).
- Résultat : pile saine en 39 s au premier démarrage (`installation-2026-11-09.log`) ; ports sur `127.0.0.1` seulement (`ports-2026-11-09.txt`) ; RAM de la pile seule 3,7 Gio au repos, 5,1 Gio en pointe pendant l'indexation du corpus (`ressources-2026-11-09-*.txt`, banc d'essai de l'adaptateur) ; vérification minimale réussie (réponse citée en 3,2 s).
- Incidents : `DataSet.parse_documents` du SDK a rendu « DONE » avec 0 passage au premier essai (`installation-2026-11-09-verif-essai1.log`) ; `Session.ask` du SDK répond 404 pour un assistant (`installation-2026-11-09-verif.log`). Contournements dans `outils/ragflow/client.py`.
- Prochaine étape : banc par défaut (phase F avancée pour nourrir les manuels), puis manuels.

### 2026-11-09 18:40 — Phases E, F et G (en cours)

- Fait : banc complet et variantes (`serie_banc.sh`) : défaut 33/34, vecteurs 0,7 et `top_n` 8 34/34, gabarits Paper 33, Table 33, Presentation 32, Agentic 30/34, contexte 4096 33/34, 3072 21/34. Notation des citations resserrée aux passages `[ID:n]` puis série rejouée (résultats identiques). Cycle désinstallation et réinstallation chronométré. Jeu de démonstration (`demo.py`). Essais : passages et DeepDoc, agent, sitemap (refus puis autorisé temporairement), Knowledge Compilation (carte mentale, graphe). Exemples exécutés (`exemples/ragflow/sorties_verifiees.txt`). Manuels 00 à 10 et 12 rédigés, captures Playwright.
- Incidents : droits d'exécution perdus à l'extraction du kit (`nettoyer.sh` code 126) ; compte créé par l'API inutilisable dans le navigateur (mot de passe à envoyer en base64) ; interface en anglais tant que le sélecteur de langue n'est pas utilisé ; deux valeurs de configuration mal enregistrées par `banc.py` (contexte, poids des vecteurs), corrigées dans les JSON avec une note ; boucle de suivi de la compilation qui attendait un état inexistant.
- Écart de méthode : un commit (manuel 04) est passé avec 1 point de `verifier_docs.py` (lien vers `docs/README.md` pas encore écrit), corrigé au commit suivant ; depuis, chaque commit dépend du code de sortie du vérificateur.
- Prochaine étape : manuels 11, 13, 14 (sauvegarde et restauration à tester), README, LICENSE, présentation, relecture adversariale, rapport.

### 2026-11-09 19:05 — Phase H : clôture

- Fait : manuels 11, 13 et 14 (recette d'ingestion, sauvegarde et restauration, API d'administration testées), présentation, README, LICENSE, rapport. Nettoyage des artefacts d'essai (`nettoyer_essais.py`), jeu de démonstration gardé (base, assistant et trois conversations « Démo Vélanor », agent démo, carte mentale).
- Relecture adversariale par un sous-agent neuf : environ 95 affirmations confirmées, 21 écarts. Traitement : preuves archivées (`outils/resultats/ragflow/preuves-2026-11-09/` : arguments et débit de vLLM, port 8080, disque MySQL, textes des captures, gabarits de compilation, état, journal du serveur sans accès sortant mentionné ; `essai-2026-11-09-sdk-defauts.log`) ; valeurs corrigées (indexation 52 à 56 s, prompt de 1 841 à 3 301 jetons, réservation GPU 80 % et 5 %, unités en Gio) ; profil sans GPU recalculé avec les mesures de `qwen3:4b-instruct` (30 à 50 s par question à 4 096 jetons) au lieu de celles de ministral ; requalifications (premier essai de carte mentale non archivé, absence d'envoi réseau en [Estimation], « 4 096 suffit, 3 072 échoue »).
- Résultat : `verifier_docs.py` à 0 point (`outils/resultats/ragflow/verifier-docs-2026-11-09.txt`).
- Prochaine étape : preuves du critère de fin (§10), commit final.
