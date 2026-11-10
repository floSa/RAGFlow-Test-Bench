# Banc ragflow — agentic — 2026-11-09T17:44:48

| Mesure | Valeur |
|---|---|
| questions | 38 |
| exactes | 30 |
| sur | 34 |
| refus_corrects | 4 |
| pieges | 4 |
| citation_bon_document | 28 |
| citation_bonne_page | 20 |
| citations_avec_page | 21 |
| juge_llm_oui | 0 |
| juge_llm_sur | 0 |
| erreurs | 0 |
| latence_p50_s | 4.61 |
| latence_p95_s | 9.05 |
| par_type | {'tableau': '8/10', 'fait simple': '11/13', 'scan': '4/4', 'anglais': '2/2', 'multi-documents': '3/3', 'audio': '2/2', 'piège': '4/4'} |
| pic_ram_mo | {'rag-ragflow-server': 1736, 'rag-ragflow-es01': 2691, 'rag-ragflow-mysql': 527, 'rag-ragflow-minio': 97, 'rag-ragflow-kvrocks': 23, 'rag-ragflow-nats': 9, 'vllm-central': 6660, 'vllm-embed': 4176, 'rag-speaches': 1342} |
| pic_ram_application_mo | 5083 |
| vram | 15254 Mo / 16380 Mo (nvidia-smi, mesuré en fin de banc) |
| indexation_s | None |

| Id | Type | Exacte | Juge LLM | Doc. cité | Latence (s) | Réponse (début) |
|---|---|---|---|---|---|---|
| Q01 | tableau | oui | - | True | 11.75 | <think>Le chiffre d'affaires de Vélanor pour l'année 2025 est de 48,6 millions d |
| Q02 | fait simple | oui | - | True | 8.12 | <think>Vélanor a été fondée en 2014 à Nantes [ID:0].The user is asking for the f |
| Q03 | fait simple | oui | - | True | 9.94 | <think>The user is asking for the name of the president of the company "Vélanor" |
| Q04 | fait simple | oui | - | True | 6.21 | <think>Le siège de Vélanor est situé au 12 quai de la Fosse, à Nantes [ID:0].The |
| Q05 | tableau | oui | - | True | 6.56 | <think>Au 31 décembre 2025, Vélanor comptait un effectif total de 412 salariés [ |
| Q06 | tableau | non | - | False | 1.12 | <think>Je ne peux pas répondre à cette question car je n'ai accès à aucune donné |
| Q07 | tableau | non | - | False | 0.65 | <think>Je n'ai trouvé aucune information dans les documents consultés concernant |
| Q08 | tableau | oui | - | True | 1.84 | <think>Le prix public du modèle Erdre Cargo est de 4 290 € TTC [ID:0].</think>   |
| Q09 | tableau | oui | - | True | 4.65 | <think>Le site de Cholet emploie 97 salariés pour l'activité de fabrication des  |
| Q10 | fait simple | oui | - | True | 4.38 | <think>Les cadres sont fabriqués à partir d'aluminium recyclé à 82 % [ID:0].</th |
| Q11 | fait simple | oui | - | True | 3.0 | <think>Le taux de recyclage des batteries usagées collectées atteint 96 %, ce qu |
| Q12 | tableau | oui | - | False | 4.17 | <think>Le fournisseur de moteurs est Motodrive Co., et il est installé à Taïwan. |
| Q13 | tableau | oui | - | True | 3.33 | <think>Le résultat net de Vélanor pour l'année 2025 s'établit à 3,1 M€ [ID:0].</ |
| Q14 | fait simple | oui | - | True | 4.3 | <think>Le taux de retour sous garantie s'établit à 1,8 % des vélos vendus, selon |
| Q15 | scan | oui | - | True | 5.02 | <think>Le prix unitaire des batteries 48V 14 Ah prévu par le contrat avec Batter |
| Q16 | scan | oui | - | True | 4.89 | <think>Le délai de livraison prévu par le contrat d'approvisionnement n°BX-2025- |
| Q17 | scan | oui | - | True | 5.0 | <think>Le plafond des pénalités de retard dans le contrat d'approvisionnement en |
| Q18 | scan | oui | - | True | 5.29 | <think>Le contrat d'approvisionnement entre Velanor SAS et Batterix GmbH prévoit |
| Q19 | fait simple | oui | - | True | 4.72 | <think>Les batteries doivent être stockées entre 10 °C et 25 °C, dans le local B |
| Q20 | fait simple | oui | - | True | 4.7 | <think>La procédure de charge et de stockage des batteries est sous la responsab |
| Q21 | tableau | oui | - | True | 3.52 | <think>L'inspection du local B2 doit avoir lieu le premier lundi de chaque mois, |
| Q22 | fait simple | oui | - | True | 1.52 | <think>Le prix public du Vilaine Compact est de 2 490 € TTC [ID:0].</think>  Le  |
| Q23 | fait simple | oui | - | True | 9.05 | <think>The user is asking for the planned capacity of the Saint-Nazaire factory  |
| Q24 | tableau | oui | - | True | 4.61 | <think>Le stock actuel de batteries BAT-48V-14Ah est de 1240 unités, et le seuil |
| Q25 | fait simple | oui | - | True | 3.93 | <think>Le cadre est garanti pour une durée de 7 ans [ID:0].</think>  Le cadre es |
| Q26 | fait simple | non | - | False | 0.99 | <think>Je n'ai pas accès à une base de données contenant les numéros de téléphon |
| Q27 | fait simple | non | - | False | 0.9 | <think>Je ne dispose pas d'informations concernant le montant de la prime d'inté |
| Q28 | anglais | oui | - | True | 1.76 | <think>The overall score Batterix obtained at the supplier audit was 87 out of 1 |
| Q29 | anglais | oui | - | True | 4.48 | <think>Le taux de cellules défectueuses mesuré chez Batterix lors de l'audit est |
| Q30 | multi-documents | oui | - | True | 5.54 | <think>Le délai de livraison contractuel de Batterix est de 21 jours après la co |
| Q31 | multi-documents | oui | - | True | 4.74 | <think>Le score d'audit obtenu par Batterix est de 87 sur 100 [ID:0]. Le contrat |
| Q32 | multi-documents | oui | - | True | 5.76 | <think>Vélanor vise un chiffre d'affaires de 55 M€ en 2026 [ID:0]. De plus, une  |
| Q33 | audio | oui | - | False | 5.59 | <think>La ligne d'assemblage numéro 3 de Nantes sera arrêtée pour maintenance du |
| Q34 | audio | oui | - | True | 4.3 | <think>Julien Moreau est le directeur de production chez Vélanor [ID:0].</think> |
| Q35 | piège | oui | - | - | 7.29 | <think>Le document consulté est un rapport annuel fictif pour 2025 et ne contien |
| Q36 | piège | oui | - | - | 4.42 | <think>Le directeur financier de Vélanor n'est pas mentionné dans les documents  |
| Q37 | piège | oui | - | - | 0.67 | <think>Je n'ai trouvé aucune information dans ma base de données concernant le n |
| Q38 | piège | oui | - | - | 5.12 | <think>Le salaire de Karim Benali n'est pas mentionné dans les documents consult |
