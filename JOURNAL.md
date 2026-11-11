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

### 2026-11-09 19:08 — Fin de mission

- Critère de fin du §10 vérifié et montré : rapport présent avec les rubriques de la phase H ; `verifier_docs.py` à 0 point ; six exemples dans `exemples/ragflow/sorties_verifiees.txt` ; neuf bancs `banc-*.json` ; `http://127.0.0.1:8088/` en HTTP 200 et santé « ok » ; ports de `rag-ragflow-server` sur `127.0.0.1` seulement ; README, LICENSE, présentation (deux configurations minimales) et `versions-2026-11-09.json` présents ; `git status` propre.
- RAGFlow laissé en marche avec le jeu de démonstration. Aucun `git push` (interdit par la fiche).

### 2026-11-11 11:10 — Manuels utilisateur, lot 1 : carte de l'interface, manuels 00 à 02

- Fait : scénario `outils/ragflow/captures/carte.py` (parcours de chaque page et menu, connecté et en français, fenêtres de création ouvertes puis fermées sans enregistrer) ; `docs/ragflow/carte-interface.md` (35 captures de repérage, textes et inventaires dans `outils/resultats/ragflow/captures/carte/`) ; plan des manuels complété (Recherche en manuel 15 prévu ; Mémoire, MCP vers 08 ; Gestion des fichiers vers 03 ; Sources de données et Canaux de chat vers 09 ; page API vers 10 ; Équipe et Profil vers 13). Manuel 00 : visite générale (3 captures annotées). Manuel 01 : procédure à la souris (inscription, « Fournisseurs de modèles », ajout puis suppression d'une instance « Manuel-instance » pointant sur `vllm-embed`, modèles par défaut ; 10 captures). Manuel 02 réécrit en procédure complète à la souris (22 captures, base « Manuel-Prise-en-main » et assistant « Manuel-Assistant » créés à la souris). Outil `outils/ragflow/nettoyer_manuel.py`.
- Résultat : `verifier_docs.py` sans point sur les fichiers du lot (points restants : manuels 04 à 14, traités par d'autres lots). Analyse des deux fichiers du manuel 02 en moins de 7 s (`outils/resultats/ragflow/captures/02-prise-en-main/scenario.log`).
- Incident : `vllm-central` (LLM-Service) redémarre en boucle depuis le matin (« No available memory for the cache blocks », 2,6 Go de VRAM déjà pris, dont le conteneur `watch-speaches` d'un autre projet). Non touché (hors enveloppe). Conséquence : l'envoi de la question à « Manuel-Assistant » n'est pas fait ; le manuel 02 montre la réponse citée de la conversation de démonstration « Contrat Batterix » et marque l'étape [À tester]. À rejouer quand `vllm-central` sera sain : `outils/communs/captures/lancer.sh outils/ragflow/captures/captures.py prise_en_main` (phases base, assistant, envoi), puis mettre à jour la section 6 du manuel 02 et lancer `nettoyer_manuel.py`.
- Objets d'essai : base « Manuel-Prise-en-main », assistant « Manuel-Assistant » et instance « Manuel-instance » supprimés (instance à la souris, les deux autres par `nettoyer_manuel.py`) ; jeu de démonstration intact.
- Reste pour d'autres lots : `docs/ragflow/img/02-prise-en-main/06-passages.png` (ancienne capture non annotée) n'est plus utilisée que par le manuel 04 ; à remplacer lors de la reprise du manuel 04.
- Prochaine étape : manuels 03 à 14 (captures annotées), manuel 15 « Applications de recherche ».

### 2026-11-11 12:26 — Manuel 02 : question réelle

- Scénario `prise_en_main` rejoué de zéro après réparation de `vllm-central` : réponse citée de « Manuel-Assistant » (1 150 euros, Q27) en 3,4 s, captures 21 et 22 réelles, mention [À tester] et capture de démonstration retirées ; objets « Manuel-… » supprimés (`nettoyer_manuel.py`).

### 2026-11-11 13:58 — Manuels utilisateur, lot 2 : manuels 03 à 06

- Fait : scénario `outils/ragflow/captures/manuels_03_06.py` (scénarios `decoupage`, `deepdoc`, `assistants`, `agentique`, tout à la souris, objets « Manuel-… »), chaque manuel rejoué de zéro avec son journal (`outils/resultats/ragflow/captures/<manuel>/scenario.log`). Manuel 03 : 52 captures (base, fichiers, gabarit par fichier, réanalyse, métadonnées, actions groupées, « Configuration » réglage par réglage, « Journaux », « Gestion des fichiers », pipelines intégrés). Manuel 04 : 19 captures (scan, journal d'analyse, passages lus, désactivés, ajoutés, test de récupération avant et après). Manuel 05 : 34 captures (paramètres du chat, test de récupération, conversation citée, actions, suppression groupée, pièce jointe, « Plusieurs modèles », intégration). Manuel 06 : 4 captures (sélecteur ouvert, question Q30 en Agentic puis en Naive). Anciennes captures non annotées retirées (dont `img/02-prise-en-main/06-passages.png`), anciens scénarios de `captures.py` retirés. Carte de l'interface et plan complétés.
- Résultats : tableur 2 → 10 passages avec « Table » ; scan analysé en 10,8 s ; passage ajouté à 83,17 contre 34,55 pour le passage OCR au test de récupération ; Q30 juste en Naive avec vecteurs 0,7 et « Top N » 8 ; Agentic (réglages par défaut) : délai contractuel trouvé deux fois sur deux, délai constaté une fois sur deux, environ 32 000 jetons d'entrée contre 1 524 en Naive.
- Défauts observés : « Confirmer » de « Modifier le segment » sans effet sur un passage de PDF modifié (aucune requête, fenêtre ouverte ; même geste enregistré sur un passage Markdown) ; pas de renommage des conversations ; libellé « Save » non traduit. Jeton `auth=` du code d'intégration masqué sur les captures et retiré des textes archivés.
- Non couvert : recherche web (compte en ligne), micro, synthèse vocale (modèles absents), analyseurs PDF externes.
- `verifier_docs.py` : 0 point sur les fichiers du lot (9 points restants, manuels 07 à 14). Objets « Manuel-… » supprimés (`nettoyer_manuel.py`, dossier de « Gestion des fichiers » supprimé à la souris) ; jeu de démonstration intact.
- Prochaine étape : manuels 07 à 14, manuel 15.

### 2026-11-11 15:59 — Manuels utilisateur, lot 3 : manuels 07, 08, 09 et 15

- Fait : scénario `outils/ragflow/captures/manuels_07_15.py` (scénarios `compilation`, `agents`, `sources`, `recherche`, tout à la souris, objets « Manuel-… ») ; anciens scénarios `agents` et `compilation` de `captures.py` et anciennes captures non annotées retirés ; `nettoyer_manuel.py` étendu (agents, pipelines, opérateurs de compilation, recherches, mémoires, sources). Manuel 07 : 36 captures (opérateur « Graph », pipeline Parser, Chunker, Compiler, Indexeur créé depuis un blanc et publié, base reliée par « Mode d'analyse », artefacts, échecs, vues). Manuels 08 (15 captures), 09 (11) et 15 (10, nouveau) : une capture par écran nouveau, selon la règle donnée en cours de lot. Index, plan, parcours du README et carte de l'interface mis à jour.
- Résultats : compilation « Graph » en 8 s (4 entités, 0 relation), « Tree » 142 s (1 nœud résumé exact), « Timeline » 5 s (2 éléments) ; « Wiki » (deux fois) et « PageIndex » en échec, « LLM response is not parseable JSON » (`gemma4:e4b`), document à 0 passage. Agent depuis le gabarit : réponses justes en anglais en 5,4 s (« Exécuter ») et 6,3 s (« Lancer ») ; mémoire « brut » remplie moins de 10 s après la réponse. Sitemap du site local : test et synchronisation refusés (« URL resolves to a non-public address »), `ALLOW_ANY_HOST` laissé à 0. Recherche : passages en moins d'une seconde, résumé juste (1 150 euros).
- Défauts observés : le canevas n'affiche pas le Compiler d'un pipeline créé par l'API et l'enregistrement automatique l'en retire (brouillon de « Essai-KC-mind_map-1835 » touché par un repérage, remis par `PUT /api/v1/agents/{id}` depuis la version publiée ; une version non publiée en plus, version publiée intacte ; `outils/resultats/ragflow/captures/07-knowledge-compilation/incident-pipeline-demo.txt`) ; la croix d'un outil dans le panneau d'un agent le retire sans confirmation ; Échap ferme toute la fenêtre « Créer une mémoire » ; heures en temps universel dans les détails de tâche et l'historique des versions ; surlignage des résultats de recherche qui coupe les mots ; recherches connexes à moitié en anglais.
- Non couvert : serveur MCP réel, relecture d'une mémoire par « Retrieval », branchement d'un canal de chat (compte en ligne), sources en ligne.
- Jetons : `auth=` des codes d'intégration masqués sur les captures et remplacés par `<masqué>` dans les textes et journaux archivés (un journal du manuel 15 corrigé avant commit).
- Objets « Manuel-… » supprimés (`nettoyage.log` de chaque manuel), site `rag-site-test` supprimé ; jeu de démonstration en place. `verifier_docs.py` : 0 point sur les fichiers du lot (5 points restants, manuels 10 à 14).
- Prochaine étape : manuels 10 à 14.

### 2026-11-11 16:27 — Manuels utilisateur, lot 4 : manuels 10 à 14

- Fait : scénario `outils/ragflow/captures/manuels_10_14.py` (scénarios `cles`, `recettes`, `qualite`, `exploitation`, `depannage`, plus `reperage` non versionné) et préparation côté WSL `outils/ragflow/manuels_10_14_preparer.py` (assistant d'essai « Manuel-Reglages », recette d'ingestion rejouée dans « Manuel-Ingestion »). Une capture par écran nouveau, renvois aux manuels 03, 05, 06 et 07 pour les écrans déjà montrés. Manuel 10 : 4 captures (page « API », fenêtre « Clé API » avec clés masquées, confirmation de suppression, documentation intégrée). Manuel 11 : 3 (base et assistant « Démo Vélanor » ouverts sans question, base remplie par la recette). Manuel 12 : 2 (jetons et durée en gros plan, « Tokens maximum » de « Modifier le modèle ») et section « Préconisations d'usage » ; tableaux du banc et profils gardés. Manuel 13 : 9 (menu du compte et « Équipe », invitation refusée puis acceptée et retirée, « Profil », « Edit Time Zone », console d'administration `/admin` : connexion, « Services », « Utilisateurs », « Bac à sable »). Manuel 14 : 4 erreurs provoquées (connexion refusée, « ERROR: prompt uses 2696 tokens… » avec le contexte à 1 024, réponse « not found », page 404) ; « Artifacts » vide renvoyé au manuel 07. Carte de l'interface (plus aucun « prévu », lignes « Modifier le modèle », console d'administration, page 404) et plan mis à jour.
- Résultats : clé d'API créée puis supprimée à la souris, clé des scripts intacte ; réponse en 1,9 s (1 834 jetons d'entrée) avec les réglages conseillés ; recette d'ingestion : 2 fichiers en 3 s, 0, puis 1 en 3 s, aucun doublon.
- Découvertes : console d'administration accessible par l'interface à `/admin` (absente de la carte faute de lien) ; elle marque « Délai Expiré » le serveur, l'ingesteur et le synchroniseur alors que l'API répond ; fuseau du compte « Asia/Shanghai » par défaut ; invitation d'une adresse sans compte refusée (« 102 user not found »).
- Incidents : première passe du scénario `cles` sans gestion de la confirmation de suppression, clé d'essai laissée puis supprimée par l'API (`captures/10-api-et-sdk/nettoyage.log`) ; un remplacement de texte mal borné a gonflé le script de captures, reconstruit avant tout commit.
- Contexte : réduit à 1 024 puis remis à 16 384 (`captures/14-depannage/contexte.log`, contrôlé après nettoyage). Objets « Manuel-… » supprimés (`captures/lot4/nettoyage.log`) ; jeu de démonstration intact. `verifier_docs.py` : 0 point.
- Prochaine étape : relecture d'ensemble des manuels 00 à 15.

### 2026-11-11 16:35 — Captures élaguées, manuels 03, 05 et 07

- Fait : une capture par action ou écran nouveau, sans nouvelle prise de vue ; doublons et écrans quasi identiques remplacés par une phrase ou un renvoi (mesures, renvois et étiquettes gardés, numéros d'étapes cités par les manuels 06 et 08 conservés). Manuel 03 : 52 → 20 ; manuel 05 : 34 → 13 ; manuel 07 : 36 → 15 ; images inutilisées retirées. `verifier_docs.py` : 0 point.

### 2026-11-11 18:02 — Manuel utilisateur en deux parties, seconde moitié : chapitres 09 à 16, annexes A1 à A6, nettoyage

- Fait : partie 1, chapitres 09 (recherche), 10 (agents, mémoire, MCP), 11 (synthèses automatiques, échecs « Wiki » et « PageIndex » expliqués), 12 (sources externes, refus des adresses privées et réglage `ALLOW_ANY_HOST` avec son risque, canaux de chat), 13 (équipe, profil, fuseau, clés d'accès, console `/admin`), 14 (deux cas pratiques nommés par leur but), 15 (erreurs avec capture, cause, remède, renvois), 16 (glossaire de 44 termes) au gabarit du §6, sans étiquettes ni renvois aux résultats bruts. Partie 2 : annexes A1 à A6 au format de preuve, avec tout le contenu technique et les preuves des anciens manuels (A6 : tableau des preuves par chapitre, affirmations étiquetées, essais par l'API, 23 défauts de RAGFlow). Carte de l'interface renvoyée vers les nouveaux chapitres. Liens corrigés (README racine avec lien vers le manuel en tête et nouveau « Le parcours », RAPPORT, docs/README.md, page d'accueil du manuel, chapitre 02 vers A4).
- Captures : 162 dans la partie 1 (01 : 0, 02 : 1, 03 : 15, 04 : 19, 05 : 10, 06 : 29, 07 : 11, 08 : 6, 09 : 10, 10 : 16, 11 : 14, 12 : 11, 13 : 12, 14 : 3, 15 : 5, 16 : 0), 2 en annexes (A1, A3) ; chacune une seule fois ; aucune image inutilisée. Fenêtre « Modifier le modèle » déplacée de A1 vers le chapitre 15 (remède à l'erreur de contexte) ; fenêtre « Publier » montrée au chapitre 10, reprise par renvoi au chapitre 11.
- Retirés : anciens manuels `docs/ragflow/00-*.md` à `15-*.md`, `presentation.md`, `plan-des-manuels.md` (contenu repris ; historique dans git).
- `verifier_docs.py` : 0 point avant chaque commit. Un commit par chapitre et par annexe, puis carte, liens et nettoyage, tous poussés.
- Reste ouvert : relecture par un lecteur novice de la partie 1 restructurée et relecture adversariale des annexes (§4 phase H, §10 point 9).

### 2026-11-11 18:45 — Relecture novice de la partie 1 : corrections

- Fait : trois bloquants (chapitre 02 : installation de LLM-Service, `.env` avec `bge-m3` et `VLLM_EXTRA_ARGS=--kv-cache-memory=700000000` ; chapitre 05 : création de la base et de l'assistant « Démo Vélanor », `demo.py` en option au 02 ; chapitre 03 : tableau des trois instances et étape « Tokens maximum », capture retirée du 15), quinze gênants et les mineurs, un commit par point. Chapitre 02 renuméroté (uv, LLM-Service), chapitres 10 (export) et 13 (invitation) aussi, renvois des autres chapitres mis à jour.
- Vérifié dans l'interface (`outils/ragflow/captures/relecture_novice.py`, journaux `outils/resultats/ragflow/captures/relecture/`) : retrait d'un modèle confirmé par « Retirer » ; modèles par défaut enregistrés dès le choix (`PATCH /api/v1/models/default`, aucun bouton) ; page de connexion « Se connecter » quand le français est mémorisé ; menu « Gestion » d'un agent et export `<nom>.json` ; invitation acceptée côté invité (« Accepter », « Refuser », « Opéré ») ; base en « Équipe » visible et ouvrable par l'invité. « Top N » 8 à la création à la souris : relevé existant (`captures/05-assistants-et-citations/scenario.log`).
- Captures : `01-inscription` et `06-modeles-listes` refaites, `08-agents/16-menu-gestion` et `13-exploitation/10-invitation-recue` nouvelles.
- Nettoyage : objets « Manuel-… » supprimés (`nettoyer_manuel.py`), compte invité désactivé puis supprimé par l'API d'administration ; jeu de démonstration intact. `verifier_docs.py` : 0 point avant chaque commit.
- Non vérifié : remède `.wslconfig` pour `vm.max_map_count` (machine d'essai à 1 048 576) ; partage d'un agent en « Équipe ».

### 2026-11-11 19:20 — Seconde relecture novice de la partie 1 : corrections

- Fait (décision de l'utilisateur) : le manuel ne fait plus installer de serveur de modèles ; chapitre 02, prérequis « serveur de modèles existant », vérification par `curl …/v1/models`, serveur de transcription facultatif (`outils/communs/voix.sh`, étape 5) ; installation de LLM-Service déplacée en annexe A2, section 8. Chapitre 03 : section « Les modèles : ceux qu'on branche, ceux qui sont intégrés » (tableau des types, reranker, DeepDoc, tokenizer, Elasticsearch, autres services, chiffres des annexes A4 et A5), branchement d'un serveur existant, modèle personnalisé (« … » › « Ajouter un modèle personnalisé »), étape « Déclarer les trois instances ».
- Gênants et mineurs corrigés, un commit par chapitre : 04 (durées, « Fermer »), 05 (neuf captures, renvois, chemin exact de l'étape 24), 06 (rappel de la base, menu situé, étape 22), 07 (assistant « Manuel-Agentic », préambule « ID » : vient du modèle, `internal/service/kb_prompt.go` numérote les passages), 08 (dix captures), 09 et 07 (« Avant : 05 »), 10 (export et import de « Manuel-Agent-Documentaire », origine de « Agent démo Vélanor » : `essai_agent.py`), 11 (deux captures), 12 (site de test avant l'étape 1 ; `arreter.sh` puis `demarrer.sh`, vérifié par `up -d --dry-run`), 13 (flux d'invitation complet, renumérotation, renvois du 15), 14 (`compte.json`), 16 (sept termes), README.
- Captures : nouvelles prises (`outils/ragflow/captures/relecture_novice_2.py`, journaux `outils/resultats/ragflow/captures/relecture-2/`) : 03 (07 refaite, 11 à 14), 07 (23, lecture seule sur « Démo Vélanor »), 10 (16, 11, 17), 13 (02, 03) ; 29 captures élaguées le 11 novembre restaurées depuis l'historique git pour les étapes qui montrent un écran nouveau (textes de page déjà dans `outils/resultats/`). Partie 1 : 194 captures. Retirées : `04-deepdoc/10-passage-desactive`, `13-exploitation/02-invitation-refusee`.
- Nettoyage : « Manuel-instance », agents « Manuel-Agent-Documentaire » et « Manuel-Agent-Importe » supprimés, compte « Manuel-Invite » désactivé puis supprimé (API d'administration) ; jeu de démonstration intact. `verifier_docs.py` : 0 point avant chaque commit.
- Non fait : capture du chapitre 04, étape 15, non refaite (« Fermer » visible sans pastille). Non vérifié : branchement d'un serveur Ollama et d'un reranker, `configurer.py` modifié pour Ollama, transcription sans serveur de voix.
