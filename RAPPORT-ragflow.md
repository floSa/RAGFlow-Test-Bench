# Rapport de mission — RAGFlow

Mission : `kit/PROMPT.md` pour la fiche `kit/fiches/02-ragflow.md`, exécutée le 9 novembre 2026 sur la machine de profil B (Ryzen 5 9600X, 32 Go de RAM dans WSL2, RTX 4060 Ti 16 Go, Ubuntu 24.04.5, Docker 29.9.3). Suivi détaillé : [JOURNAL.md](JOURNAL.md).

## Sommaire

1. [Ce qui a été installé](#1-ce-qui-a-été-installé)
2. [Où ouvrir la solution](#2-où-ouvrir-la-solution)
3. [Manuels écrits](#3-manuels-écrits)
4. [Résultats du banc](#4-résultats-du-banc)
5. [Vérifié, non vérifié](#5-vérifié-non-vérifié)
6. [Incidents](#6-incidents)
7. [Décisions en attente](#7-décisions-en-attente)
8. [Disque, RAM et VRAM](#8-disque-ram-et-vram)
9. [Arrêter ou tout supprimer](#9-arrêter-ou-tout-supprimer)
10. [Proposition pour la solution suivante](#10-proposition-pour-la-solution-suivante)
11. [Ce qui reste ouvert](#11-ce-qui-reste-ouvert)

## 1. Ce qui a été installé

| Élément | Version | Empreinte ou source |
|---|---|---|
| RAGFlow (sources au tag) | v1.0.0, dernière stable | commit `db1cd5929a7885a3074547791f5ecc4d2f891739`, dans `sources/ragflow/` (ignoré par git) |
| Image RAGFlow | `infiniflow/ragflow:v1.0.0` | `sha256:ed8dff41a7530ed8fb037fe7479a7c535429d42fa8d00aec28b54bcbc056934d` |
| Elasticsearch | 8.11.3 (imposée par le compose) | `sha256:58a3a280935d830215802322e9a0373faaacdfd646477aa7e718939c2f29292a` |
| MySQL | 8.0.40 (imposée) | `sha256:d58ac93387f644e4e040c636b8f50494e78e5afc27ca0a87348b2f577da2b7ff` |
| MinIO (`pgsty/silo`) | RELEASE.2026-08-06T00-00-00Z (imposée) | `sha256:29a498b24669cae1fed11c1a2fb2b3d73c68829a0a9c0b14e71b386671d38fac` |
| Kvrocks | 2.16.0 (imposée) | `sha256:9e632c317c83c80d92f1c9d22ac6aa9f64d149e1f04ff2af5f15a5768a01c4b7` |
| NATS | 2.14.2 (imposée) | `sha256:bbfbb6c4cdaeb8a2e3ca57d3de30463a66a6c5181f324f3b680bcf858833d377` |
| SDK Python | `ragflow-sdk` 1.0.0, Python 3.13 (uv) | `pyproject.toml`, `uv.lock` |
| Modèles (LLM-Service, non modifié) | `gemma4:e4b` (Gemma 4 E4B w4a16) et `bge-m3` sur vLLM 0.29.0 | branche `service-vllm` |
| Transcription | `Systran/faster-whisper-small` sur `rag-speaches` (socle de la série) | `outils/communs/voix.sh` |
| Captures | `mcr.microsoft.com/playwright/python:v1.64.1-noble` | figée par empreinte dans `outils/communs/captures/lancer.sh` |

Aucun modèle téléchargé (modèles déjà servis par LLM-Service ; modèles DeepDoc embarqués dans l'image). Téléchargements : images de la pile (3,1 Go), image Playwright, image `ollama/ollama` figée tirée par le test GPU du diagnostic (5,6 Go au plus) : moins de 15 Go au total, sous le plafond de 150 Go. Versions relevées : [versions-2026-11-09.json](outils/resultats/ragflow/versions-2026-11-09.json).

## 2. Où ouvrir la solution

- Interface : **http://127.0.0.1:8088** dans le navigateur Windows (8080 était déjà occupé par un autre programme de la machine). Langue : sélecteur « English » puis « Français » dans l'en-tête.
- Identifiants locaux fictifs, clé d'API et accès d'administration : `donnees/IDENTIFIANTS-LOCAUX.txt`.
- Jeu de démonstration : base « Démo Vélanor » (9 documents, 26 passages), assistant « Démo Vélanor » avec trois conversations citées (« Contrat Batterix », « Objectifs 2026 », « Audit fournisseur »), agent « Agent démo Vélanor », base « Essai-KC-mind_map-1835 » (onglet « Artifacts », « Mind map »).
- Vérification depuis WSL : `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/` renvoie 200 ; `outils/ragflow/etat.sh`.

## 3. Manuels écrits

Page d'accueil du manuel : [docs/ragflow/README.md](docs/ragflow/README.md) ; série et comparatif : [docs/README.md](docs/README.md).

| Partie | Contenu |
|---|---|
| 1. Manuel utilisateur | 16 chapitres à lire dans l'ordre : [01. Découvrir RAGFlow](docs/ragflow/manuel/01-decouvrir-ragflow.md), [02. Installer](docs/ragflow/manuel/02-installer-ragflow.md), [03. Premiers pas](docs/ragflow/manuel/03-premiers-pas.md), [04. Première question](docs/ragflow/manuel/04-premiere-question.md), [05. Documents](docs/ragflow/manuel/05-ajouter-et-organiser-ses-documents.md), [06. Lecture des documents](docs/ragflow/manuel/06-regler-la-lecture-des-documents.md), [07. Questions et sources](docs/ragflow/manuel/07-poser-des-questions-et-lire-les-sources.md), [08. Régler un assistant](docs/ragflow/manuel/08-regler-un-assistant.md), [09. Rechercher](docs/ragflow/manuel/09-rechercher.md), [10. Agents](docs/ragflow/manuel/10-agents.md), [11. Synthèses automatiques](docs/ragflow/manuel/11-syntheses-automatiques.md), [12. Sources externes](docs/ragflow/manuel/12-sources-externes.md), [13. Comptes, équipe et clés](docs/ragflow/manuel/13-comptes-equipe-et-cles.md), [14. Cas pratiques](docs/ragflow/manuel/14-cas-pratiques.md), [15. En cas de problème](docs/ragflow/manuel/15-en-cas-de-probleme.md), [16. Glossaire](docs/ragflow/manuel/16-glossaire.md) |
| 2. Évaluation et compléments | [A1. Qualité et performances](docs/ragflow/annexes/A1-evaluation-qualite-et-performances.md), [A2. Matériel et modèles](docs/ragflow/annexes/A2-choisir-son-materiel-et-ses-modeles.md), [A3. API](docs/ragflow/annexes/A3-automatiser-par-l-api.md), [A4. Exploitation](docs/ragflow/annexes/A4-exploitation.md), [A5. Fonctionnement interne](docs/ragflow/annexes/A5-fonctionnement-interne.md), [A6. Rapport d'essais](docs/ragflow/annexes/A6-rapport-d-essais.md) |

Manuel utilisateur refait le 11 novembre 2026 : chaque action faite à la souris, 196 captures annotées (rectangle rouge, pastille numérotée, tableau N° | Élément | Rôle), carte de l'interface dans [docs/ragflow/annexes/carte-interface.md](docs/ragflow/annexes/carte-interface.md) (4 éléments non couverts, raison donnée). Exemples exécutés : `exemples/ragflow/` et [sorties vérifiées](exemples/ragflow/sorties_verifiees.txt).

## 4. Résultats du banc

1. Réglages par défaut : 33 bonnes réponses sur 34, 4 refus corrects sur 4 pièges, bon document cité 34 fois, bonne page 24 sur 24 ([banc](outils/resultats/ragflow/banc-2026-11-09-defaut.md)).
2. Poids des vecteurs 0,7 et `top_n` 8 : 34 sur 34 ([banc](outils/resultats/ragflow/banc-2026-11-09-hybride-vecteurs07-top8.md)).
3. Temps de réponse : 1,28 s en médiane, 1,88 s au 95e centile ; indexation du corpus en 53 s.
4. Le PDF scanné est lu (4 sur 4) ; Open Notebook, sur le même socle GPU, faisait 27 sur 34.
5. Mode agentique moins bon (30 sur 34, 4,5 s) ; contexte de 4 096 jetons suffisant, 3 072 trop court (21 sur 34).

## 5. Vérifié, non vérifié

| Vérifié par l'essai | Non vérifié, et pourquoi |
|---|---|
| installation, réinstallation et désinstallation complètes chronométrées | mise à jour : aucune version plus récente que v1.0.0 |
| ports sur `127.0.0.1` seulement | reranking : aucun reranker dans le socle, LLM-Service partagé |
| compte, clé d'API, modèles déclarés par l'API ; interface en français | second modèle et modèle de moins de 3 milliards de paramètres : LLM-Service sert un seul modèle de réponse, partagé |
| banc complet et 8 variantes (gabarits, réglages, agentique, contexte) | profil A sans GPU : chiffres [Estimation] à partir des mesures CPU du socle |
| OCR et correction des passages ; carte mentale et graphe compilés | Wiki, Tree, PageIndex, Timeline ; gabarit Picture (aucun modèle `image2text` déclaré) |
| agent depuis un gabarit, API et SDK ; sitemap (refus, puis autorisé le temps d'un essai) | gabarits d'agents demandant le web ; resynchronisation complète (`rebuild`) |
| sauvegarde et restauration ; API d'administration ; six exemples | effet de la langue « English » par défaut de la base sur la recherche en français |

La relecture adversariale par un sous-agent neuf et ses corrections sont consignées au journal.

## 6. Incidents

| Incident | Effet | Traitement |
|---|---|---|
| Droits d'exécution perdus à l'extraction de l'archive du kit | `nettoyer.sh` en code 126, premier cycle de réinstallation sans effet | `chmod +x`, cycle rejoué |
| Compte créé par l'API avec mot de passe en clair | connexion refusée dans le navigateur | mot de passe envoyé en base64, réinstallation |
| SDK 1.0.0 : `Session.ask` en 404 pour un assistant ; `parse_documents` prématuré une fois | questions et attente impossibles par le SDK seul | contournements dans `outils/ragflow/client.py` |
| `reference.chunks` contient tous les passages fournis | notation des citations trop large dans la première série | notation resserrée aux `[ID:n]`, série rejouée (même résultat) |
| Deux réglages mal relevés par `banc.py` (contexte, poids des vecteurs) | configuration fausse dans deux JSON | corrigée dans les JSON avec une note, script corrigé |
| Boucle de suivi de compilation sur un état inexistant | essai arrêté à la main | condition de fin corrigée, essai rejoué |
| Un commit passé avec 1 point de `verifier_docs.py` | manuel 04 lié à un index pas encore écrit | corrigé au commit suivant |

## 7. Décisions en attente

1. **Montée de vLLM** dans LLM-Service (0.29.0 en service, 0.32.0 disponible) : non faite, pour ne pas toucher un service partagé et garder la comparaison avec le banc Open Notebook.
2. **Port de l'interface** : 8088 au lieu de 8080 ; libérer 8080 (processus Python de l'utilisateur) ou garder 8088.
3. **`git push`** : interdit par la fiche ; aucun dépôt distant configuré. À créer et pousser à la main (`https://github.com/floSa/RAGFlow-Test-Bench` selon la convention de la série).
4. **Reranker** : ajouter un serveur de reranking à LLM-Service pour essayer le reranking ?
5. **Ports `0.0.0.0` hors mission** : `vllm-central`, `vllm-embed` et `watch-speaches` sont publiés sur toutes les interfaces ; à ramener sur `127.0.0.1` dans leurs propres dépôts.

## 8. Disque, RAM et VRAM

| Mesure | Valeur |
|---|---|
| Images de la pile | 3,1 Go |
| Données `donnees/ragflow/` | 1,3 Go (dont 1 Go de journal de reprise MySQL préalloué) |
| Sauvegarde gardée | 41 Mo dans `donnees/sauvegardes/` |
| RAM de l'application, en fin de mission | 3 867 Mio, soit 3,8 Gio (pointe mesurée : 5 394 Mio, 5,3 Gio) |
| RAM de LLM-Service | `vllm-central` 6,5 Gio, `vllm-embed` 4,1 Gio |
| VRAM | 15 250 Mio sur 16 380 (LLM-Service) |

[Mesures de fin de mission](outils/resultats/ragflow/ressources-2026-11-09-fin-de-mission.txt).

## 9. Arrêter ou tout supprimer

```bash
outils/ragflow/arreter.sh
outils/ragflow/demarrer.sh
outils/communs/nettoyer.sh ragflow
```

`arreter.sh` garde les données ; `nettoyer.sh` supprime conteneurs, volumes, réseau et `donnees/ragflow/` (14 s mesurées), sans toucher à LLM-Service ni aux images. Open Notebook a été arrêté au début de la mission (`~/mes_projets/Tutoriels/Open-Notebook-Test-Bench/outils/open-notebook/arreter.sh`) ; le relancer par son `demarrer.sh` si besoin.

## 10. Proposition pour la solution suivante

Kotaemon (fiche 03), pour vérifier les citations dans le PDF. Avant de la lancer : arrêter RAGFlow (`outils/ragflow/arreter.sh`), préparer le dépôt avec `outils/communs/nouvelle_solution.sh` en corrigeant au passage les chemins `~/Projets` en `~/mes_projets` et les droits d'exécution, et reprendre `outils/communs/banc/tableau.py`, désormais générique, pour le comparatif. Le banc gagnerait à noter les citations sur les seules sources réellement citées par la réponse, comme ici.

## 11. Ce qui reste ouvert

| Sujet | État |
|---|---|
| Non traité | mise à jour de version (aucune plus récente que v1.0.0) ; reranking ; second modèle et modèle de moins de 3 milliards de paramètres ; synthèses « Wiki » et « PageIndex » en échec avec `gemma4:e4b` (chapitre [11](docs/ragflow/manuel/11-syntheses-automatiques.md)) ; gabarit « Picture » ; modèles d'agents qui demandent Internet |
| Estimé, non mesuré | configuration sans carte graphique (annexe [A2](docs/ragflow/annexes/A2-choisir-son-materiel-et-ses-modeles.md)) |
| Décisions en attente | montée de vLLM dans LLM-Service ; port 8088 au lieu de 8080 ; reranker ; ports ouverts sur tout le réseau par des services hors mission (section 7) |
| Ménage à faire à la main | images Docker gardées en cache ; sauvegarde de test dans `donnees/sauvegardes/` |
| Écarts de version | moteur de recherche, mémoire tampon, file d'attente et stockage à la version du fichier officiel (Elasticsearch 8.11.3, Kvrocks 2.16.0, NATS 2.14.2, MinIO d'août 2026) : plus récentes disponibles, non montées sans essai |
| Relectures | relecture par un lecteur novice de la partie 1 faite le 11 novembre 2026 et corrigée (journal) ; relecture adversariale des annexes à refaire sur le manuel restructuré |
