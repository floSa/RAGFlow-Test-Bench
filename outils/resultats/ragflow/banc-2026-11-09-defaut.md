# Banc ragflow — defaut — 2026-11-09T17:40:59

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
| latence_p50_s | 1.3 |
| latence_p95_s | 2.41 |
| par_type | {'tableau': '10/10', 'fait simple': '13/13', 'scan': '4/4', 'anglais': '2/2', 'multi-documents': '2/3', 'audio': '2/2', 'piège': '4/4'} |
| pic_ram_mo | {'rag-ragflow-server': 1860, 'rag-ragflow-es01': 2650, 'rag-ragflow-mysql': 521, 'rag-ragflow-minio': 103, 'rag-ragflow-kvrocks': 23, 'rag-ragflow-nats': 9, 'vllm-central': 6658, 'vllm-embed': 4178, 'rag-speaches': 1345} |
| pic_ram_application_mo | 5166 |
| vram | 15247 Mo / 16380 Mo (nvidia-smi, mesuré en fin de banc) |
| indexation_s | 56.0 |

| Id | Type | Exacte | Juge LLM | Doc. cité | Latence (s) | Réponse (début) |
|---|---|---|---|---|---|---|
| Q01 | tableau | oui | - | True | 2.9 | Le chiffre d'affaires de Vélanor pour 2025 était de 48,6 M€ [ID:1][ID:3]. Les ch |
| Q02 | fait simple | oui | - | True | 0.47 | Vélanor a été fondée en 2014 [ID:0]. |
| Q03 | fait simple | oui | - | True | 0.68 | La présidente de Vélanor est Hélène Marchais, et elle dirige l'entreprise depuis |
| Q04 | fait simple | oui | - | True | 1.21 | Le siège de Vélanor est situé au 12 quai de la Fosse, à Nantes [ID:0]. |
| Q05 | tableau | oui | - | True | 2.41 | Vélanor comptait 412 salariés au 31 décembre 2025 [ID:3]. Les effectifs par site |
| Q06 | tableau | oui | - | True | 1.79 | Le chiffre d'affaires du troisième trimestre (T3) 2025 a été de 14,2 M€ [ID:0].  |
| Q07 | tableau | oui | - | True | 1.3 | Le modèle Sèvre Trail a vu 15 400 unités produites en 2025 [ID:0]. |
| Q08 | tableau | oui | - | True | 1.15 | Le prix public TTC du modèle Erdre Cargo est de 4 290 € [ID:0]. |
| Q09 | tableau | oui | - | True | 1.21 | Le site de Cholet emploie 97 salariés pour l'activité de fabrication des cadres  |
| Q10 | fait simple | oui | - | True | 1.24 | Les cadres sont fabriqués à partir d'aluminium recyclé à 82 % [ID:0]. |
| Q11 | fait simple | oui | - | True | 1.49 | Le taux de recyclage des batteries usagées collectées atteint 96 %, ce qui est r |
| Q12 | tableau | oui | - | True | 1.37 | Le fournisseur qui livre les moteurs est Motodrive Co., et il est installé au Ta |
| Q13 | tableau | oui | - | True | 1.27 | Le résultat net de Vélanor s'établit à 3,1 M€ en 2025 [ID:2]. |
| Q14 | fait simple | oui | - | True | 1.33 | Le taux de retour sous garantie s'établit à 1,8 % des vélos vendus [ID:0]. |
| Q15 | scan | oui | - | True | 1.74 | Le prix unitaire pour la fourniture de batteries 48V 14 Ah, référence BAT-48V-14 |
| Q16 | scan | oui | - | True | 1.14 | Le délai de livraison prévu est de 21 jours après la commande [ID:1]. |
| Q17 | scan | oui | - | True | 1.33 | Le plafond des pénalités de retard dans le contrat avec Batterix est fixé à 8% d |
| Q18 | scan | oui | - | True | 1.27 | Le volume minimal annuel de batteries prévu par le contrat Batterix est de 40 00 |
| Q19 | fait simple | oui | - | True | 1.57 | Les batteries doivent être stockées entre 10 °C et 25 °C, dans le local B2 équip |
| Q20 | fait simple | oui | - | True | 1.5 | Karim Benali, responsable HSE, est le responsable de la Procédure PR-SEC-04 rela |
| Q21 | tableau | oui | - | True | 1.18 | Le local B2 est inspecté le premier lundi de chaque mois [ID:0]. |
| Q22 | fait simple | oui | - | True | 1.22 | Le prix public du Vilaine Compact est de 2 490 € TTC [ID:0]. |
| Q23 | fait simple | oui | - | True | 1.42 | La capacité prévue de l'usine de Saint-Nazaire est de 25 000 vélos par an [ID:0] |
| Q24 | tableau | oui | - | True | 1.68 | Le stock restant de batteries BAT-48V-14Ah est de 1240 unités, et son seuil d'al |
| Q25 | fait simple | oui | - | True | 1.03 | Le cadre est garanti 7 ans [ID:0]. |
| Q26 | fait simple | oui | - | True | 1.68 | Le service après-vente peut être joint par téléphone au 02 40 00 12 34, du lundi |
| Q27 | fait simple | oui | - | True | 1.56 | Le prime d'intéressement 2025 est de 1 150 euros par salarié, et elle sera versé |
| Q28 | anglais | oui | - | True | 1.2 | The overall score Batterix obtained at the supplier audit was 87 out of 100 [ID: |
| Q29 | anglais | oui | - | True | 1.17 | Le taux de défaut des cellules mesuré est de 0,3 % [ID:0]. |
| Q30 | multi-documents | non | - | True | 1.6 | Le dataset fournit le délai moyen constaté de livraison pour Batterix GmbH, mais |
| Q31 | multi-documents | oui | - | True | 1.68 | Batterix a obtenu un score de 87 sur 100 lors de l'audit [ID:2] et le prix unita |
| Q32 | multi-documents | oui | - | True | 2.06 | Vélanor vise un chiffre d'affaires de 55 M€ en 2026 [ID:2][ID:0]. De plus, il es |
| Q33 | audio | oui | - | True | 1.34 | La ligne d'assoblage numéro 3 de Nantes sera arrêtée pour maintenance du 2 au 6  |
| Q34 | audio | oui | - | True | 1.08 | Julien Moreau est le directeur de production chez Vélanor [ID:1]. |
| Q35 | piège | oui | - | - | 1.04 | The answer you are looking for is not found in the dataset! [ID:5] |
| Q36 | piège | oui | - | - | 0.43 | The answer you are looking for is not found in the dataset! [ID:2] |
| Q37 | piège | oui | - | - | 2.66 | L'information concernant le nombre de trottinettes électriques vendues par Vélan |
| Q38 | piège | oui | - | - | 1.02 | The answer you are looking for is not found in the dataset! [ID:2] |
