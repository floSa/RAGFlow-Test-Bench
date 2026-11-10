#!/usr/bin/env bash
# Essai de sauvegarde et restauration : sauvegarde, création d'une base témoin, restauration,
# vérification que la base témoin a disparu et que la démonstration répond toujours.
# Usage : outils/ragflow/essai_sauvegarde.sh   Journal : outils/resultats/ragflow/essai-<date>-sauvegarde.log
set -uo pipefail
cd "$(dirname "$0")/../.."
exec > >(tee "outils/resultats/ragflow/essai-$(date +%F)-sauvegarde.log") 2>&1
liste() { uv run python -c "import sys; sys.path.insert(0,'outils/ragflow'); from client import client; print(sorted(d.name for d in client().list_datasets()))"; }
t=$(date +%s); echo "== $(date -Iseconds) sauvegarde"; outils/ragflow/sauvegarder.sh; echo "-> $(( $(date +%s) - t )) s"
arch=$(ls -t donnees/sauvegardes/ragflow-*.tar.gz | head -1)
uv run python -c "import sys; sys.path.insert(0,'outils/ragflow'); from client import client; client().create_dataset(name='Témoin-après-sauvegarde')"
echo "bases avant restauration : $(liste)"
t=$(date +%s); echo "== $(date -Iseconds) restauration"; outils/ragflow/restaurer.sh "$arch"; echo "-> $(( $(date +%s) - t )) s"
echo "bases après restauration : $(liste)"
uv run python - <<'PY'
import sys; sys.path.insert(0, "outils/ragflow")
from client import client, demander
chat = client().list_chats(name="Démo Vélanor")[0]
s = chat.create_session("après restauration")
r, d = demander(chat.id, s.id, "Quel est le prix public du Vilaine Compact ?")
print(f"question à la démonstration après restauration ({d:.1f} s) : {r['data']['answer']}")
chat.delete_sessions(ids=[s.id])
PY
