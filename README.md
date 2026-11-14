# RAGFlow

Interroger ses propres documents, scans compris, avec une IA qui cite le passage et la page, sur sa machine, sans service en ligne.

Ce dépôt contient le service (`service/`, pour lancer RAGFlow sous Docker), le banc d'essai (`banc-essai/`, 38 questions) et la documentation avec le manuel utilisateur (`documentations/`).

```text
RAGFlow-Test-Bench/
├── README.md
├── LICENSE
│
├── service/                 lancer RAGFlow (Docker)
│   ├── installer.sh         première installation
│   ├── demarrer.sh
│   ├── arreter.sh
│   └── …                    état, sauvegarde, réglages
│
├── banc-essai/              rejouer les tests
│   ├── corpus/              9 documents et 38 questions
│   ├── ragflow/             scripts du banc et des captures propres à RAGFlow
│   ├── communs/             outils partagés par les cinq bancs
│   ├── exemples/            appels à l'API, avec leurs sorties vérifiées
│   └── resultats/           scores et preuves brutes
│
└── documentations/          lire
    ├── README.md            sommaire du manuel
    ├── manuel/              le guide, chapitre par chapitre
    ├── annexes/             évaluation, matériel, API, exploitation
    ├── img/                 captures d'écran
    ├── index-serie.md       comparaison des cinq solutions
    ├── fiche-technique.md   architecture, réglages, versions, licences
    ├── rapport.md           bilan
    └── journal.md           avancement
```

Les fichiers locaux, ignorés par git, restent à la racine : `donnees/` (volumes et identifiants), `sources/` le cas échéant.

## Lancer le service

Prérequis : Docker, le service de modèles LLM-Service en marche, sa clé dans `service/.env` (copie de `service/.env.example`).

```bash
cd service
./installer.sh     # première fois seulement
./demarrer.sh
./arreter.sh
```

## Rejouer le banc

Le service doit tourner.

```bash
uv sync --project banc-essai
uv run --project banc-essai python banc-essai/ragflow/banc.py --etiquette defaut --reindexer
```

## Lire la documentation

| Besoin | Page |
|---|---|
| Utiliser RAGFlow pas à pas | [Manuel](documentations/README.md) |
| Installer | [Chapitre 02](documentations/manuel/02-installer-ragflow.md) |
| Résultats détaillés du banc | [Annexe A1](documentations/annexes/A1-evaluation-qualite-et-performances.md) |
| Comparer aux quatre autres solutions | [Index de la série](documentations/index-serie.md) |
| Architecture, réglages, versions, licences | [Fiche technique](documentations/fiche-technique.md) |
| Bilan | [Rapport](documentations/rapport.md) |

## Résultats

Banc de 38 questions (34 avec réponse, 4 pièges), modèles du service central : Qwen3.5-4B avec réflexion, bge-m3, bge-reranker-v2-m3.

| Réglage | OCR | Recherche | Passages | Reranker | Exactes /34 | Pièges refusés /4 | Médiane | Pic RAM de l'application |
|---|---|---|---|---|---|---|---|---|
| défaut | DeepDoc | hybride, vecteurs 0,3 | 6 |  | 33 | 4 | 7,8 s | 5,4 Go |
| meilleur | DeepDoc | hybride, vecteurs 0,7 | 8 |  | 34 | 4 | 7,8 s | 5,1 Go |

Le reranker bge-reranker-v2-m3 rattrape la question manquée avec le réglage par défaut, mais n'ajoute rien au meilleur réglage.

Toutes les variantes : [annexe A1](documentations/annexes/A1-evaluation-qualite-et-performances.md). Méthode et preuves : [annexe A6](documentations/annexes/A6-rapport-d-essais.md). Bilan : [documentations/rapport.md](documentations/rapport.md). Comparaison avec les quatre autres solutions : [index de la série](documentations/index-serie.md).
