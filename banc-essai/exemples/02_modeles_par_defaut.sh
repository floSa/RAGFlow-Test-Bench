#!/usr/bin/env bash
# Modèles par défaut du compte (clé d'API lue dans donnees/ragflow/compte.json, jamais affichée).
CLE=$(python3 -c "import json; print(json.load(open('donnees/ragflow/compte.json'))['api_key'])")
curl -s -H "Authorization: Bearer $CLE" http://127.0.0.1:9380/api/v1/models/default |
  python3 -c "import json,sys; [print(m['model_type'], '->', m['model_name'], '@', m['model_instance'], '(', m['model_provider'], ')') for m in json.load(sys.stdin)['data']['models']]"
