#!/usr/bin/env bash
# Exécute chaque exemple depuis la racine du dépôt et ajoute sa sortie réelle à sorties_verifiees.txt.
set -uo pipefail
cd "$(dirname "$0")/../.."
S=exemples/ragflow/sorties_verifiees.txt
echo "# Sorties vérifiées des exemples RAGFlow — $(date -Iseconds) — RAGFlow v1.0.0, ragflow-sdk 1.0.0" > "$S"
for f in exemples/ragflow/[0-9][0-9]_*; do
  echo; echo "## $(basename "$f")"
  case "$f" in *.sh) bash "$f";; *.py) uv run python "$f";; esac 2>&1
  echo "(code de sortie $?)"
done >> "$S"
cat "$S"
