#!/usr/bin/env bash
# Archive des preuves demandées par la relecture adversariale : arguments et débit de vLLM, port 8080, détail du
# disque MySQL, textes de pages relevés par les captures, gabarits de compilation intégrés, état, recherche
# d'accès réseau sortants dans les journaux du serveur.
# Usage : outils/ragflow/preuves_complementaires.sh   Sorties : outils/resultats/ragflow/preuves-<date>/
set -uo pipefail
cd "$(dirname "$0")/../.."
D="outils/resultats/ragflow/preuves-$(date +%F)"
mkdir -p "$D/textes-captures"
{ echo "== arguments de lancement (journal de vllm-central)"; docker logs vllm-central 2>&1 | grep -m1 "non-default args"
  echo "== arguments de lancement (journal de vllm-embed)"; docker logs vllm-embed 2>&1 | grep -m1 "non-default args"
  echo "== mémoire GPU (journal de vllm-central)"; docker logs vllm-central 2>&1 | grep -m1 "Desired GPU memory utilization"
  echo "== débit de génération : 15 dernières lignes non nulles"; docker logs vllm-central 2>&1 | grep "generation throughput" | grep -v "generation throughput: 0.0" | tail -15
} > "$D/vllm-extrait.log"
{ echo "== $(date -Iseconds) ports en écoute sur 8080 (processus de l'utilisateur, non touché)"; ss -ltnp 2>/dev/null | grep -E ':8080\b' || echo "8080 libre"; } > "$D/port-8080.txt"
docker run --rm -v "$PWD/donnees/ragflow/mysql:/m:ro" nginx:alpine sh -c 'du -sh /m/* | sort -h' > "$D/mysql-disque.txt"
cp donnees/captures-explorer/*.txt "$D/textes-captures/" 2>/dev/null
uv run python -c "
import sys, json; sys.path.insert(0, 'outils/ragflow'); from client import http
b = http('GET', '/compilation-templates/builtins')['data']
print(json.dumps([{k: t.get(k) for k in ('id', 'kind', 'display_name')} for t in b], ensure_ascii=False, indent=1))" > "$D/compilation-builtins.json"
outils/ragflow/etat.sh > "$D/etat.txt" 2>&1
{ echo "== recherche, dans tout le journal du serveur, de mentions d'hôtes externes"
  docker logs rag-ragflow-server 2>&1 | grep -ciE "hf-mirror|huggingface\.co|download" | sed 's/^/lignes contenant hf-mirror, huggingface.co ou download : /'
  docker logs rag-ragflow-server 2>&1 | grep -iE "hf-mirror|huggingface\.co|download" | head -5
  echo "lignes au total dans le journal : $(docker logs rag-ragflow-server 2>&1 | wc -l)"; } > "$D/acces-sortants.txt"
ls -la "$D" "$D/textes-captures" | awk '{print $5, $NF}'
