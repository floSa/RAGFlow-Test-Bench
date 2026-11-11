# 16. Glossaire

> Ce chapitre définit simplement chaque mot employé dans le manuel, avec le libellé que lui donne l'interface quand il diffère, et le chapitre où la notion est expliquée.
> **Point de départ** : aucun écran ; à consulter à tout moment.
> **Durée** : à la demande. **Avant** : aucun.

## Ce qu'il faut savoir

L'interface de RAGFlow mélange le français et l'anglais, et donne parfois deux noms à la même chose : une base de connaissances s'appelle aussi « dataset » ou « Ensemble de données », un passage « segment » ou « chunk ». Le tableau ci-dessous donne pour chaque terme le mot du manuel, puis entre guillemets les libellés de l'interface. Les termes communs à toutes les solutions de la série figurent aussi dans le [glossaire de la série](../../glossaire.md).

## Les termes

| Terme | Définition simple | Chapitre |
|---|---|---|
| Agent | Enchaînement de blocs dessiné sur un canevas, dont au moins un bloc interroge un modèle d'IA qui décide seul d'appeler des outils (chercher dans une base, sur le web…). Plus libre qu'un assistant, mais plus lent. | 10 |
| Analyse | Étape où RAGFlow lit un document, le découpe en passages et les range pour la recherche. Un document non analysé ne peut pas être cité. Interface : « Analyser ». | 04, 05 |
| Artefact | Voir « Synthèse ». | 11 |
| Assistant | Interlocuteur relié à une ou plusieurs bases : il cherche les passages utiles, les donne au modèle et fait rédiger une réponse citée. Interface : « Discussion », « chat ». | 04, 07, 08 |
| Bac à sable | Endroit isolé où s'exécute le code lancé par un agent, réglé dans la console d'administration. Interface : « Bac à sable ». | 13 |
| Base de connaissances | Ensemble de documents interrogés ensemble, avec leur façon d'être lus. Interface : « Base de connaissances », « dataset », « Ensemble de données ». | 04, 05 |
| Canal de chat | Publication d'un assistant ou d'un agent dans une messagerie (Telegram, Discord…). Interface : « Canaux de chat ». | 12 |
| Canevas | Page en plein écran où se dessine un agent ou une chaîne de lecture, bloc par bloc. | 10, 11 |
| Chaîne de lecture | Suite d'étapes appliquée à chaque document d'une base : lecture, découpage, éventuellement synthèse, rangement pour la recherche. Les gabarits en sont des versions toutes faites. Interface : « Ingestion pipeline », « pipeline d'ingestion ». | 06, 11 |
| Citation | Petit numéro entre crochets (« [1] ») après une phrase de la réponse ; il renvoie au passage qui la justifie. | 04, 07 |
| Clé d'accès | Code secret qui permet à un programme d'agir au nom d'un compte, sans mot de passe ; toute clé a tous les droits du compte. Interface : « Clé API ». | 13 |
| Console d'administration | Partie de l'interface réservée au compte `admin@ragflow.io`, à l'adresse `/admin` : comptes et services de l'installation. | 13 |
| Conteneur | Programme isolé lancé par Docker ; RAGFlow en utilise six (application, base de données, moteur de recherche, stockage des fichiers, mémoire tampon, file d'attente). | 02 |
| DeepDoc | Lecteur de documents intégré à RAGFlow : il reconnaît les caractères des scans, repère titres, colonnes et tableaux, sur la machine elle-même. | 06 |
| Document | Fichier ajouté à une base : PDF, Word, tableur, présentation, page web, note, fichier audio… Interface : « Fichiers ». | 04, 05 |
| Embedding | Traduction du sens d'un texte en une suite de nombres ; deux textes de sens proche ont des nombres proches. C'est ce qui permet la recherche par le sens. Interface : « Modèle d'embedding ». | 03 |
| Équipe | Groupe de comptes invités qui partagent les objets dont les « Autorisations » valent « Équipe ». | 13 |
| Fournisseur, instance | Un fournisseur est un type de service de modèles (« VLLM », « Ollama »…) ; une instance est une adresse précise de ce service, déclarée sous un nom libre. Interface : « Fournisseurs de modèles ». | 03 |
| Gabarit | Façon de découper un type de document : texte suivi, tableur ligne par ligne, présentation diapositive par diapositive… Interface : « Mode d'analyse », « pipeline intégré », « (built in) ». | 06 |
| Jeton | Unité dans laquelle un modèle compte le texte, à peu près une syllabe. L'interface affiche les jetons lus et écrits sous chaque réponse. Interface : « tokens ». | 04 |
| LLM-Service | Serveur de modèles de la machine d'essai, installé à part (dépôt séparé) et partagé avec d'autres applications ; il sert désormais, par LiteLLM, `chat`, `embed`, `rerank` et `transcribe` (ancienne pile : `gemma4:e4b` et `bge-m3` par vLLM). Le manuel ne le fait pas installer : tout serveur de modèles existant convient. | 02, 03, annexe A2 |
| MCP | Façon standard de proposer des outils (agenda, logiciel métier…) à un modèle d'IA ; un serveur MCP déclaré ajoute ses outils aux agents. | 10 |
| Mémoire | Lieu où un agent garde ses échanges d'une session à l'autre, pour les retrouver ensuite par le sens. Interface : « Mémoire ». | 10 |
| Métadonnées | Informations ajoutées à un document (auteur, service, date…) qui permettent de filtrer la recherche. | 05, 08 |
| Mode « Naive », mode « Agentic » | Deux façons de répondre d'un assistant : « Naive » cherche une fois puis rédige (rapide, conseillé) ; « Agentic » laisse le modèle chercher en plusieurs fois (plus lent, moins juste avec un petit modèle). | 07 |
| Modèle d'IA | Programme qui rédige les réponses (« Modèle de chat ») ou qui traduit le sens d'un texte en nombres (« Modèle d'embedding ») ; d'autres transcrivent l'audio ou décrivent les images. | 03 |
| Modèle de second tri | Modèle qui reclasse les passages trouvés pour mettre les plus utiles en tête ; aucun n'est installé ici. Interface : « Modèle de rerank », « Modèle de réordonnancement ». | 03, 08 |
| Ollama | Logiciel libre qui fait tourner des modèles d'IA sur la machine, avec ou sans carte graphique, et les rend accessibles aux autres applications par une adresse web. RAGFlow le branche par le fournisseur « Ollama » ; non essayé ici. | 02, 03 |
| Opérateur de synthèse | Recette qui dit quelle synthèse produire (graphe, arbre, frise, carte mentale…) et avec quelles consignes. Interface : « Compilation operator », « Template ». | 11 |
| Passage | Morceau de document, de quelques lignes à une page, que RAGFlow retrouve et transmet au modèle. Interface : « segment », « chunk ». | 04, 06 |
| Plan de site | Fichier `sitemap.xml` qui liste les pages d'un site web ; une source « Sitemap » le relit pour remplir une base. | 12 |
| Poids des mots-clés | Part donnée à la recherche par les mots exacts ; le reste va à la recherche par le sens. Réglage conseillé : 0,3, soit 0,7 pour le sens. Interface : « Poids de similarité par mots-clés ». | 08 |
| Prompt système | Consignes fixes données au modèle avant chaque question : rôle de l'assistant, façon de citer, phrase de refus ; le mot `{knowledge}` y marque l'endroit où sont insérés les passages trouvés. Interface : « Prompt système ». | 08 |
| RAG | Méthode qui retrouve d'abord les passages utiles dans les documents, puis les donne au modèle pour qu'il réponde à partir d'eux et les cite. C'est le principe de RAGFlow. | 01 |
| Recherche | Page de recherche sur une ou plusieurs bases, sans conversation : passages trouvés, résumé, questions voisines, carte mentale. Interface : « Recherche ». | 09 |
| Recherche par les mots, par le sens | La première retrouve les passages qui contiennent les mots de la question ; la seconde ceux qui en ont le sens, même avec d'autres mots. RAGFlow combine les deux (recherche hybride). | 01, 08 |
| Reconnaissance de caractères | Lecture du texte d'une image ou d'un scan ; elle peut confondre des signes (« 0 » et « o »). Aussi appelée OCR. | 06 |
| Regex (expression régulière) | Motif qui décrit une famille de textes, par exemple `^https://example\.com/docs/` pour « toutes les adresses qui commencent par https://example.com/docs/ ». Interface : « Filtre d'URL (regex) ». | 12 |
| Reranker | Voir « Modèle de second tri ». Interface : type « Rerank ». | 03, 08 |
| Serveur de modèles | Programme qui fait tourner les modèles d'IA (Ollama, vLLM, LM Studio…) et répond aux demandes de RAGFlow par une adresse web ; RAGFlow n'en contient pas et doit être branché sur un serveur existant. | 02, 03 |
| Seuil de similarité | Score minimal qu'un passage doit atteindre pour être retenu. Interface : « Seuil de similarité ». | 08, 09 |
| Source de données | Système extérieur (site web, wiki, stockage…) que RAGFlow relit régulièrement pour garder une base à jour. Interface : « Sources de données », « connecteur ». | 12 |
| Synchronisation | Relecture d'une source de données ; chacune laisse une ligne dans le journal. | 12 |
| Synthèse | Résultat tiré automatiquement des documents d'une base : graphe de connaissances, arbre de résumés, frise, carte mentale, table des matières, wiki. Interface : « Artifacts », « artefact ». | 11 |
| Taille de contexte | Quantité de texte qu'un modèle peut lire d'un coup : consignes, passages, question et réponse. Les essais déclarent 16 384 jetons. Interface : « Tokens maximum ». | 03, 15 |
| Test de récupération | Outil d'une base qui montre les passages trouvés pour une question, sans faire rédiger de réponse. Interface : « Test de récupération ». | 08 |
| Top N | Nombre de passages donnés au modèle pour rédiger la réponse ; réglage conseillé : 8. Interface : « Top N ». | 08 |
| uv | Outil qui installe Python et les bibliothèques d'un projet, puis lance ses scripts : `uv sync` prépare le dossier, `uv run python …` lance un script. | 02 |
| vLLM | Logiciel libre qui fait tourner des modèles d'IA sur une carte graphique NVIDIA, plus vite qu'Ollama ; il répond comme un serveur compatible OpenAI. C'est le serveur des essais de ce manuel ; fournisseur « VLLM » dans RAGFlow. | 02, 03 |
| WSL2 | Sous-système Linux de Windows, dans lequel tournent Docker et RAGFlow. | 02 |

## Bon à savoir

- Quand un mot de l'interface reste en anglais (« Sign in », « Save draft », « Artifacts »), le manuel le cite tel qu'il s'affiche.
- Les termes techniques plus poussés (découpage, recherche hybride, services internes) sont détaillés dans l'annexe [A5. Fonctionnement interne](../annexes/A5-fonctionnement-interne.md).

---
*Version décrite : RAGFlow v1.0.0, essais des 9 et 11 novembre 2026. Détails et preuves : [rapport d'essais](../annexes/A6-rapport-d-essais.md).*
