#!/usr/bin/env bash
# Reranker sur le GPU : service vllm-rerank de LLM-Service (vLLM 0.29.0, modèle BAAI/bge-reranker-v2-m3),
# à côté de vllm-central (chat) et vllm-embed (embedding), pour vérifier que les trois modèles tiennent sur 16 Go.
# - service déclaré dans ~/mes_projets/Projet-IA/LLM-Service/docker-compose.override.yml, fichier local non suivi
#   (exclu par .git/info/exclude), aucun fichier suivi de LLM-Service modifié ; image figée par empreinte ;
# - démarré seul (--no-deps) : vllm-central et vllm-embed ne sont ni recréés ni redémarrés ;
# - réseau llm-net (RAGFlow y est déjà) : http://vllm-rerank:8000/v1 ; port publié sur 127.0.0.1:8003 seulement ;
# - garde-fou : rien n'est démarré si moins de MIN_VRAM Mio sont libres sur la carte graphique.
# Essai intermédiaire sur processeur (TEI 1.8.2, conteneur rag-reranker, arrêté) : reranker_cpu.sh.
# Usage : outils/ragflow/reranker.sh [--attendre]   (--attendre : réessaie toutes les 30 s pendant 15 min)
# Journal : outils/resultats/ragflow/reranker-<date>.log
set -euo pipefail
cd "$(dirname "$0")/../.."
LLM="${LLM_SERVICE_DIR:-$HOME/mes_projets/Projet-IA/LLM-Service}"
MODELE="bge-reranker-v2-m3"
PORT=8003
MIN_VRAM=2048
J="outils/resultats/ragflow/reranker-$(date +%F).log"
exec > >(tee -a "$J") 2>&1
echo "== $(date -Iseconds) reranker.sh $*"
vram() { nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader,nounits; }
libre() { vram | awk -F', ' '{print $2}'; }
free -m | awk '/Mem:/{print "RAM disponible : " $7 " Mo"}'
if ! docker ps --format '{{.Names}}' | grep -qx vllm-rerank; then
  essais=1; [ "${1:-}" = "--attendre" ] && essais=30
  for i in $(seq "$essais"); do
    echo "$(date +%T) VRAM utilisée, libre, totale (Mio) : $(vram)"
    [ "$(libre)" -ge "$MIN_VRAM" ] && break
    [ "$i" -eq "$essais" ] && { echo "VRAM libre insuffisante (< $MIN_VRAM Mio) : vllm-rerank non démarré"; exit 2; }
    sleep 30
  done
  (cd "$LLM" && docker compose --profile rerank up -d --no-deps vllm-rerank)
fi
t0=$(date +%s)
for i in $(seq 200); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break
  docker ps --format '{{.Names}}' | grep -qx vllm-rerank || { echo "vllm-rerank arrêté"; docker logs --tail 60 vllm-rerank; exit 1; }
  sleep 3; done
curl -sf http://127.0.0.1:$PORT/health >/dev/null || { echo "vllm-rerank pas sain"; docker logs --tail 60 vllm-rerank; exit 1; }
echo "sain en $(( $(date +%s) - t0 )) s"
docker ps --filter name=vllm --format 'conteneur : {{.Names}} {{.Image}} {{.Ports}} {{.Status}}'
echo "VRAM utilisée, libre, totale (Mio), trois modèles chargés : $(vram)"
nvidia-smi
curl -s http://127.0.0.1:$PORT/v1/models | python3 -c "import json,sys;print('modèles :',[(m['id'],m.get('max_model_len')) for m in json.load(sys.stdin)['data']])"
Q='{"model":"'"$MODELE"'","query":"Quel est le délai de préavis ?","documents":["Le préavis de résiliation est de trois mois.","La cantine ouvre à midi."],"top_n":2}'
echo "POST /v1/rerank (format Jina/Cohere, celui des pilotes VLLM et OpenAI-API-Compatible de RAGFlow) : $Q"
curl -s -w '\n(%{http_code}, %{time_total} s)\n' http://127.0.0.1:$PORT/v1/rerank -H 'Content-Type: application/json' -d "$Q"
echo "depuis le conteneur rag-ragflow-server (réseau llm-net) :"
docker exec rag-ragflow-server curl -s -m 30 http://vllm-rerank:8000/v1/models -o /dev/null -w 'http://vllm-rerank:8000/v1/models -> %{http_code}\n' || true
docker stats --no-stream --format 'mémoire vive : {{.Name}} {{.MemUsage}}' vllm-rerank vllm-embed vllm-central
docker inspect vllm-rerank --format 'image : {{.Config.Image}} ; redémarrages : {{.RestartCount}}'
