# Banc ragflow — gabarit-presentation — 2026-11-09T17:50:30

| Mesure | Valeur |
|---|---|
| questions | 38 |
| exactes | 32 |
| sur | 34 |
| refus_corrects | 4 |
| pieges | 4 |
| citation_bon_document | 34 |
| citation_bonne_page | 24 |
| citations_avec_page | 24 |
| juge_llm_oui | 0 |
| juge_llm_sur | 0 |
| erreurs | 0 |
| latence_p50_s | 1.18 |
| latence_p95_s | 2.03 |
| par_type | {'tableau': '10/10', 'fait simple': '13/13', 'scan': '4/4', 'anglais': '1/2', 'multi-documents': '2/3', 'audio': '2/2', 'piège': '4/4'} |
| pic_ram_mo | {'rag-ragflow-server': 2137, 'rag-ragflow-es01': 2705, 'rag-ragflow-mysql': 529, 'rag-ragflow-minio': 110, 'rag-ragflow-kvrocks': 29, 'rag-ragflow-nats': 13, 'vllm-central': 6658, 'vllm-embed': 4177, 'rag-speaches': 1480} |
| pic_ram_application_mo | 5523 |
| vram | 15241 Mo / 16380 Mo (nvidia-smi, mesuré en fin de banc) |
| indexation_s | 56.1 |

| Id | Type | Exacte | Juge LLM | Doc. cité | Latence (s) | Réponse (début) |
|---|---|---|---|---|---|---|
| Q01 | tableau | oui | - | True | 2.03 | Le chiffre d'affaires de Vélanor pour 2025 s'est établi à 48,6 M€ [ID:3][ID:5].  |
| Q02 | fait simple | oui | - | True | 0.94 | Vélanor a été fondée en 2014 [ID:0]. |
| Q03 | fait simple | oui | - | True | 1.2 | La présidente de Vélanor est Hélène Marchais [ID:0]. Elle dirige l'entreprise de |
| Q04 | fait simple | oui | - | True | 1.09 | Le siège de Vélanor est situé au 12 quai de la Fosse, à Nantes [ID:0]. |
| Q05 | tableau | oui | - | True | 2.82 | Au 31/12/2025, Vélanor comptait un total de 412 salariés [ID:1][ID:0].  La répar |
| Q06 | tableau | oui | - | True | 1.62 | Le chiffre d'affaires pour le troisième trimestre 2025 était de 14,2 M€ [ID:0].  |
| Q07 | tableau | oui | - | True | 1.35 | Le nombre d'unités produites pour le modèle Sèvre Trail en 2025 est de 15 400 [I |
| Q08 | tableau | oui | - | True | 1.06 | Le prix public TTC du modèle Erdre Cargo est de 4 290 € [ID:0]. |
| Q09 | tableau | oui | - | True | 1.15 | Le site de Cholet emploie 97 salariés pour l'activité de fabrication des cadres  |
| Q10 | fait simple | oui | - | True | 1.18 | Les cadres sont fabriqués à partir d'aluminium recyclé à 82 % [ID:0]. |
| Q11 | fait simple | oui | - | True | 1.27 | Le taux de recyclage des batteries usagées collectées atteint 96 % grâce au part |
| Q12 | tableau | oui | - | True | 1.16 | Le fournisseur des moteurs est Motodrive Co., et il est installé en Taïwan [ID:1 |
| Q13 | tableau | oui | - | True | 1.17 | Le résultat net de Vélanor s'est établi à 3,1 M€ en 2025 [ID:5]. |
| Q14 | fait simple | oui | - | True | 1.23 | Le taux de retour sous garantie s'établit à 1,8 % des vélos vendus [ID:0]. |
| Q15 | scan | oui | - | True | 1.82 | Le prix unitaire des batteries prévu par le contrat avec Batterix est de 212 eur |
| Q16 | scan | oui | - | True | 1.52 | Le fournisseur livre sous 21 jours après la commande selon l'article 5 du contra |
| Q17 | scan | oui | - | True | 1.06 | Le plafond des pénalités de retard est fixé à 8% du montant de la commande [ID:0 |
| Q18 | scan | oui | - | True | 1.11 | Le volume minimal annuel de batteries prévu par le contrat Batterix est de 40 00 |
| Q19 | fait simple | oui | - | True | 1.4 | Les batteries doivent être stockées entre 10 °C et 25 °C, dans le local B2 qui e |
| Q20 | fait simple | oui | - | True | 1.22 | Karim Benali, responsable HSE, est le responsable de la procédure PR-SEC-04 conc |
| Q21 | tableau | oui | - | True | 1.02 | Le local B2 est inspecté le premier lundi de chaque mois [ID:0]. |
| Q22 | fait simple | oui | - | True | 1.06 | Le prix public du Vilaine Compact est de 2 490 € TTC [ID:0]. |
| Q23 | fait simple | oui | - | True | 1.3 | La capacité prévue de l'usine de Saint-Nazaire est de 25 000 vélos par an [ID:0] |
| Q24 | tableau | oui | - | True | 1.62 | Le stock actuel de la batterie BAT-48V-14Ah est de 1240 unités [ID:0]. Ce stock  |
| Q25 | fait simple | oui | - | True | 0.9 | Le cadre est garanti 7 ans [ID:0]. |
| Q26 | fait simple | oui | - | True | 1.67 | Le service après-vente peut être joint par téléphone au 02 40 00 12 34, du lundi |
| Q27 | fait simple | oui | - | True | 1.5 | Le montant de la prime d'intéressement 2025 est de 1 150 euros par salarié, et e |
| Q28 | anglais | oui | - | True | 1.01 | Batterix obtained an overall score of 87 out of 100 at the supplier audit [ID:0] |
| Q29 | anglais | non | - | True | 1.0 | The answer you are looking for is not found in the dataset! [ID:1] |
| Q30 | multi-documents | non | - | True | 2.65 | Voici les informations concernant les délais :  *   **Délai moyen constaté pour  |
| Q31 | multi-documents | oui | - | True | 1.6 | Batterix a obtenu un score global de 87 sur 100 lors de l'audit du fournisseur [ |
| Q32 | multi-documents | oui | - | True | 1.89 | Vélanor vise un chiffre d'affaires de 55 M€ en 2026 [ID:0][ID:1]. De plus, il es |
| Q33 | audio | oui | - | True | 1.34 | La ligne d'assoblage numéro 3 de Nantes sera arrêtée pour maintenance [ID:0]. Ce |
| Q34 | audio | oui | - | True | 0.95 | Le directeur de production de Vélanor est Julien Moreau [ID:0]. |
| Q35 | piège | oui | - | - | 0.92 | The answer you are looking for is not found in the dataset! [ID:4] |
| Q36 | piège | oui | - | - | 0.91 | The answer you are looking for is not found in the dataset! [ID:5] |
| Q37 | piège | oui | - | - | 0.9 | The answer you are looking for is not found in the dataset! [ID:4] |
| Q38 | piège | oui | - | - | 0.96 | The answer you are looking for is not found in the dataset! [ID:3] |
