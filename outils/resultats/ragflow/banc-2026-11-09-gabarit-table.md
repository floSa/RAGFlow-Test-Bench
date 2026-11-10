# Banc ragflow — gabarit-table — 2026-11-09T17:52:17

| Mesure | Valeur |
|---|---|
| questions | 38 |
| exactes | 33 |
| sur | 34 |
| refus_corrects | 4 |
| pieges | 4 |
| citation_bon_document | 34 |
| citation_bonne_page | 24 |
| citations_avec_page | 24 |
| juge_llm_oui | 0 |
| juge_llm_sur | 0 |
| erreurs | 0 |
| latence_p50_s | 1.21 |
| latence_p95_s | 1.83 |
| par_type | {'tableau': '10/10', 'fait simple': '13/13', 'scan': '4/4', 'anglais': '2/2', 'multi-documents': '2/3', 'audio': '2/2', 'piège': '4/4'} |
| pic_ram_mo | {'rag-ragflow-server': 2227, 'rag-ragflow-es01': 2708, 'rag-ragflow-mysql': 532, 'rag-ragflow-minio': 115, 'rag-ragflow-kvrocks': 25, 'rag-ragflow-nats': 9, 'vllm-central': 6656, 'vllm-embed': 4176, 'rag-speaches': 1687} |
| pic_ram_application_mo | 5616 |
| vram | 15249 Mo / 16380 Mo (nvidia-smi, mesuré en fin de banc) |
| indexation_s | 53.1 |

| Id | Type | Exacte | Juge LLM | Doc. cité | Latence (s) | Réponse (début) |
|---|---|---|---|---|---|---|
| Q01 | tableau | oui | - | True | 4.83 | Le chiffre d'affaires de Vélanor pour l'année 2025 s'est établi à 48,6 M€ [ID:1] |
| Q02 | fait simple | oui | - | True | 1.09 | Vélanor a été fondée en 2014 [ID:0]. |
| Q03 | fait simple | oui | - | True | 1.22 | La présidente de Vélanor est Hélène Marchais, et elle dirige l'entreprise depuis |
| Q04 | fait simple | oui | - | True | 1.16 | Le siège de Vélanor est situé au 12 quai de la Fosse, à Nantes [ID:0]. |
| Q05 | tableau | oui | - | True | 3.65 | Le nombre total de salariés de Vélanor au 31 décembre 2025 est de 412 [ID:3][ID: |
| Q06 | tableau | oui | - | True | 1.73 | Le chiffre d'affaires du troisième trimestre 2025 a été de 14,2 M€ [ID:0]. Le tr |
| Q07 | tableau | oui | - | True | 1.3 | Le modèle Sèvre Trail a produit 15 400 unités en 2025 [ID:0]. |
| Q08 | tableau | oui | - | True | 1.13 | Le prix public TTC du modèle Erdre Cargo est de 4 290 € [ID:0]. |
| Q09 | tableau | oui | - | True | 1.18 | Le site de Cholet emploie 97 salariés pour l'activité de fabrication des cadres  |
| Q10 | fait simple | oui | - | True | 1.14 | Les cadres sont fabriqués à partir d'aluminium recyclé à 82 % [ID:0]. |
| Q11 | fait simple | oui | - | True | 1.39 | Le taux de recyclage des batteries usagées collectées atteint 96 %, grâce au par |
| Q12 | tableau | oui | - | True | 1.21 | Le fournisseur qui livre les moteurs est Motodrive Co., et il est installé au Ta |
| Q13 | tableau | oui | - | True | 1.2 | Vélanor a dégagé un résultat net de 3,1 M€ en 2025 [ID:2]. |
| Q14 | fait simple | oui | - | True | 1.3 | Le taux de retour sous garantie s'établit à 1,8 % des vélos vendus [ID:0]. |
| Q15 | scan | oui | - | True | 1.31 | Le prix unitaire des batteries est fixé à 212 euros HT, avec une possibilité de  |
| Q16 | scan | oui | - | True | 1.2 | Le délai de livraison prévu par le contrat avec Batterix GmbH est de 21 jours ap |
| Q17 | scan | oui | - | True | 1.27 | Le plafond des pénalités de retard dans le contrat Batterix est fixé à 8 % du mo |
| Q18 | scan | oui | - | True | 1.24 | Le volume minimal annuel de batteries prévu par le contrat Batterix est de 40 00 |
| Q19 | fait simple | oui | - | True | 1.45 | Les batteries doivent être stockées entre 10 °C et 25 °C, dans le local B2 qui e |
| Q20 | fait simple | oui | - | True | 1.16 | Karim Benali est le responsable de la procédure de charge et de stockage des bat |
| Q21 | tableau | oui | - | True | 1.08 | Le local B2 est inspecté le premier lundi de chaque mois [ID:0]. |
| Q22 | fait simple | oui | - | True | 1.13 | Le prix public du Vilaine Compact est de 2 490 € TTC [ID:0]. |
| Q23 | fait simple | oui | - | True | 1.29 | La capacité prévue de l'usine de Saint-Nazaire est de 25 000 vélos par an [ID:0] |
| Q24 | tableau | oui | - | True | 1.82 | Le stock restant pour la référence BAT-48V-14Ah est de 1240 unités, et le seuil  |
| Q25 | fait simple | oui | - | True | 1.01 | La durée de garantie du cadre est de 7 ans [ID:0]. |
| Q26 | fait simple | oui | - | True | 1.64 | Le service après-vente peut être joint par téléphone au 02 40 00 12 34, du lundi |
| Q27 | fait simple | oui | - | True | 1.55 | La prime d'intéressement pour 2025 est de 1 150 euros par salarié, et elle sera  |
| Q28 | anglais | oui | - | True | 1.18 | Batterix GmbH obtained an overall score of 87 out of 100 during the Supplier Qua |
| Q29 | anglais | oui | - | True | 1.12 | Le taux de défaut de cellule mesuré est de 0,3 % [ID:0]. |
| Q30 | multi-documents | non | - | True | 1.43 | Le délai de livraison contractuel de Batterix n'est pas mentionné dans les docum |
| Q31 | multi-documents | oui | - | True | 1.59 | Batterix a obtenu un score de 87 sur 100 lors de l'audit [ID:2]. Le contrat fixe |
| Q32 | multi-documents | oui | - | True | 1.83 | Vélanor vise un chiffre d'affaires de 55 M€ en 2026 [ID:0][ID:2]. Pour le projet |
| Q33 | audio | oui | - | True | 1.29 | La ligne d'assoblage numéro 3 de Nantes sera arrêtée pour maintenance du 2 au 6  |
| Q34 | audio | oui | - | True | 1.05 | Le directeur de production chez Vélanor est Julien Moreau [ID:1]. |
| Q35 | piège | oui | - | - | 1.01 | The answer you are looking for is not found in the dataset! [ID:5] |
| Q36 | piège | oui | - | - | 0.4 | The answer you are looking for is not found in the dataset! [ID:2] |
| Q37 | piège | oui | - | - | 1.04 | The answer you are looking for is not found in the dataset! [ID:2] |
| Q38 | piège | oui | - | - | 0.98 | The answer you are looking for is not found in the dataset! [ID:2] |
