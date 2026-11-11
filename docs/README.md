# Index de la série

Manuels vérifiés de solutions de RAG local sous Windows 11 + WSL2. Chaque solution a son dépôt ; ce dépôt décrit RAGFlow et reprend les résultats des solutions déjà passées au banc.

## Solutions décrites

| Solution | Version décrite | Date des essais | Machine de test | Langue de l'interface | Manuels |
|---|---|---|---|---|---|
| Open Notebook | 1.15.1 | 2026-11-08 et 2026-11-09 | Intel Core Ultra 7 255H, 15,3 Go (WSL), sans GPU NVIDIA, socle Ollama sur CPU ; puis Ryzen 5 9600X, RTX 4060 Ti 16 Go, socle vLLM | français (langue du navigateur) | dépôt https://github.com/floSa/Open-Notebook-Test-Bench |
| RAGFlow | v1.0.0 | 2026-11-09 | Ryzen 5 9600X, 32 Go (WSL), RTX 4060 Ti 16 Go ; socle vLLM 0.29.0 | français (sélecteur de l'en-tête ; page de connexion en anglais) | [manuel utilisateur](ragflow/README.md) |

## Comparatif du banc

Mêmes 38 questions ([corpus/questions.json](../corpus/questions.json) : 34 avec réponse, 4 pièges sans réponse dans le corpus), même corpus fictif de 9 documents. Les lignes « gemma4:e4b » sont comparables entre elles (même modèle sur vLLM, même machine) ; la ligne « qwen3:4b-instruct » vient d'une autre machine, sur CPU. [Vérifié] (fichiers JSON liés)

| Solution | Banc | Modèle | Réglages | Exactes | Refus pièges | Bon document cité | Bonne page | p50 (s) | p95 (s) | Indexation (s) | Pic RAM application (Mo) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| open-notebook | [docling-qwen-fullcontent-ollama040](../outils/resultats/open-notebook/banc-2026-11-08-docling-qwen-fullcontent-ollama040.json) | qwen3:4b-instruct | mode chat, sources full content, num_ctx 16384, Docling true | 28/34 | 4/4 | 28 | non exposée | 7.44 | 24.19 | 84.3 | 3133 |
| open-notebook | [gpu-vllm](../outils/resultats/open-notebook/banc-2026-11-09-gpu-vllm.json) | gemma4:e4b | mode chat, sources full content, Docling false | 27/34 | 4/4 | 24 | non exposée | 1.86 | 4.28 | 54.2 | 624 |
| ragflow | [defaut](../outils/resultats/ragflow/banc-2026-11-09-defaut.json) | gemma4:e4b (vLLM, LLM-Service service-vllm) | gabarit general, top_n 6, poids vecteurs 0.3, contexte 16384 | 33/34 | 4/4 | 34 | 24/24 | 1.28 | 1.88 | 53.0 | 5394 |
| ragflow | [hybride-vecteurs07-top8](../outils/resultats/ragflow/banc-2026-11-09-hybride-vecteurs07-top8.json) | gemma4:e4b (vLLM, LLM-Service service-vllm) | gabarit general, top_n 8, poids vecteurs 0.7, contexte 16384 | 34/34 | 4/4 | 34 | 24/24 | 1.36 | 1.83 | - | 5041 |
| ragflow | [agentic](../outils/resultats/ragflow/banc-2026-11-09-agentic.json) | gemma4:e4b (vLLM, LLM-Service service-vllm) | gabarit general, top_n 6, poids vecteurs 0.3, contexte 16384, options {"reasoning": 5} | 30/34 | 4/4 | 29 | 21/21 | 4.52 | 7.22 | - | 5331 |

Lecture :

- « Bon document cité » compte les 34 questions avec réponse ; pour RAGFlow, seuls les passages marqués `[ID:n]` dans la réponse comptent.
- « Bonne page » : seul RAGFlow expose la page du passage cité (positions dans le PDF).
- La différence principale vient du PDF scanné : RAGFlow le lit (OCR DeepDoc, 4 questions sur 4), Open Notebook non.
- RAGFlow consomme bien plus de RAM (Elasticsearch, MySQL, MinIO et DeepDoc) : 5,3 Gio en pointe contre 0,6 Gio pour Open Notebook sur le même socle GPU.

## Parcours de lecture conseillés

| Profil | Parcours |
|---|---|
| Découvrir le RAG local | [glossaire](glossaire.md), puis [Découvrir RAGFlow](ragflow/manuel/01-decouvrir-ragflow.md), puis l'annexe [Fonctionnement interne](ragflow/annexes/A5-fonctionnement-interne.md) |
| Installer et essayer rapidement | chapitres [01 à 04 du manuel RAGFlow](ragflow/README.md#par-où-commencer) |
| Choisir entre solutions | comparatif ci-dessus, puis annexes [Qualité et performances](ragflow/annexes/A1-evaluation-qualite-et-performances.md) et [Matériel et modèles](ragflow/annexes/A2-choisir-son-materiel-et-ses-modeles.md) de RAGFlow |
| Automatiser | [Automatiser par l'API](ragflow/annexes/A3-automatiser-par-l-api.md) |

## Conventions

| Étiquette | Sens |
|---|---|
| [Vérifié] | observé ou mesuré sur la machine d'essai, à la date indiquée ; renvoie à un script et à un résultat brut de `outils/` |
| [Source] | lu dans la documentation officielle ou le code source, non essayé |
| [Estimation] | calcul non mesuré, avec son raisonnement |
| [À tester] | ni documenté ni essayé |
| [Testée] | commande exécutée pendant les essais |
| [Aide] | commande lue dans l'aide, non exécutée |

Les libellés de l'interface sont cités tels qu'affichés. Les données sont fictives (entreprise Vélanor).
