#!/usr/bin/env bash
# Installation rejouable et idempotente de RAGFlow v1.0.0, branché à LLM-Service (aucun serveur de modèles propre).
#  1. récupération des sources au tag figé (sources/ragflow, ignoré par git) ;
#  2. réglages et secrets générés localement (donnees/ragflow/ragflow.env, ignoré par git) ;
#  3. démarrage du projet compose rag-ragflow avec outils/ragflow/compose.override.yml ;
#  4. attente de l'état sain (/api/v1/system/healthz).
# Le compte local et le branchement des modèles sont faits ensuite par outils/ragflow/configurer.py.
# Usage : outils/ragflow/installer.sh   (journal : outils/resultats/ragflow/installation-<date>.log)
set -euo pipefail
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$RACINE"
TAG=v1.0.0
COMMIT=db1cd5929a7885a3074547791f5ecc4d2f891739
SRC="$RACINE/sources/ragflow"
DONNEES="$RACINE/donnees/ragflow"
ENVF="$DONNEES/ragflow.env"
JOURNAL="outils/resultats/ragflow/installation-$(date +%F).log"
mkdir -p "$(dirname "$JOURNAL")"
exec > >(tee -a "$JOURNAL") 2>&1
echo "== installer.sh $(date -Iseconds)"
debut=$(date +%s)

# 0. prérequis
docker compose version >/dev/null || { echo "docker compose indisponible"; exit 1; }
for r in llm-net rag-local; do
  docker network inspect "$r" >/dev/null 2>&1 || { echo "réseau $r absent : lancer LLM-Service (outils/communs/llm_service_vllm.sh) et la voix (outils/communs/voix.sh)"; exit 1; }
done
free -m | awk '/Mem:/{print "RAM disponible avant installation : " $7 " Mo"}'

# 1. sources au tag figé
if [ ! -d "$SRC/.git" ]; then
  git clone -q --depth 1 --branch "$TAG" https://github.com/infiniflow/ragflow.git "$SRC"
fi
[ "$(git -C "$SRC" rev-parse HEAD)" = "$COMMIT" ] || { echo "sources/ragflow n'est pas au commit attendu de $TAG"; exit 1; }
echo "sources : $TAG ($COMMIT)"

# 2. réglages : copie du docker/.env officiel puis écarts (la dernière valeur d'une clé l'emporte)
mkdir -p "$DONNEES"/{esdata01,mysql,minio,kvrocks,nats,logs}
if [ ! -f "$ENVF" ]; then
  secret() { openssl rand -hex 16; }
  {
    cat "$SRC/docker/.env"
    echo
    echo "# ---- écarts du banc (outils/ragflow/installer.sh), générés le $(date -Iseconds) ----"
    echo "RAGFLOW_ENV_FILE=$ENVF"
    echo "RAGFLOW_DONNEES=$DONNEES"
    echo "SVR_WEB_HTTP_PORT=8088"
    echo "TZ=Europe/Paris"
    echo "MEM_LIMIT=4294967296"
    echo "ELASTIC_PASSWORD=$(secret)"
    echo "MYSQL_PASSWORD=$(secret)"
    echo "MINIO_PASSWORD=$(secret)"
    echo "REDIS_PASSWORD=$(secret)"
    echo "ADMIN_DEFAULT_PASSWORD=$(secret)"
  } > "$ENVF"
  chmod 600 "$ENVF"
  echo "réglages générés : $ENVF"
else
  echo "réglages existants gardés : $ENVF"
fi

# 3. démarrage
DC=(docker compose -p rag-ragflow --env-file "$ENVF" -f "$SRC/docker/docker-compose.yml" -f "$RACINE/outils/ragflow/compose.override.yml")
"${DC[@]}" up -d
# 4. état sain
for i in $(seq 120); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9380/api/v1/system/healthz || true)
  [ "$code" = 200 ] && break
  sleep 5
done
echo "healthz (9380) : HTTP $code après $(( $(date +%s) - debut )) s"
curl -s http://127.0.0.1:9380/api/v1/system/healthz; echo
echo "interface : HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/)"
docker ps --filter name=rag-ragflow --format '{{.Names}} {{.Status}} {{.Ports}}'
[ "$code" = 200 ]
