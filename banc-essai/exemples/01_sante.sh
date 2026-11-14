#!/usr/bin/env bash
# État de santé de RAGFlow (sans authentification) et version de l'interface.
curl -s http://127.0.0.1:9380/api/v1/system/healthz; echo
curl -s -o /dev/null -w "interface web : HTTP %{http_code}\n" http://127.0.0.1:8088/
