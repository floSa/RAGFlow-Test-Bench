#!/usr/bin/env bash
# État de RAGFlow : conteneurs, ports, santé, modèles de LLM-Service.
cd "$(dirname "$0")/../.."
docker ps -a --filter name=rag-ragflow --format '{{.Names}}  {{.Status}}  {{.Ports}}'
echo "santé : $(curl -s -m 5 http://127.0.0.1:9380/api/v1/system/healthz || echo injoignable)"
echo "interface : HTTP $(curl -s -o /dev/null -m 5 -w '%{http_code}' http://127.0.0.1:8088/)"
for c in vllm-central vllm-embed ollama-central; do
  docker ps --format '{{.Names}}' | grep -qx $c && echo "LLM-Service : $c en marche"
done
