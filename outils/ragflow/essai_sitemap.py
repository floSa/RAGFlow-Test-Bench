"""Ingestion par sitemap d'un site local de test (conteneur nginx rag-site-test sur le réseau rag-local).

1. démarrage du site de test (pages fictives de outils/ragflow/site-test/) ;
2. création d'un connecteur « sitemap » par l'API, test du connecteur ;
3. liaison à une base d'essai et suivi de la synchronisation ;
4. suppression du connecteur, de la base et du site.
Usage : uv run python outils/ragflow/essai_sitemap.py   Sortie : outils/resultats/ragflow/essai-<date>-sitemap.log
"""
import datetime, json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, documents, http  # noqa: E402

lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} essai sitemap"]


def log(m):
    print(m, flush=True)
    lignes.append(str(m))


def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


site = RACINE / "outils/ragflow/site-test"
sh("docker", "rm", "-f", "rag-site-test")
log("site de test : " + sh("docker", "run", "-d", "--name", "rag-site-test", "--network", "rag-local",
                            "-v", f"{site}:/usr/share/nginx/html:ro", "nginx:alpine")[:12])
time.sleep(2)
log("depuis le serveur RAGFlow : " + sh("docker", "exec", "rag-ragflow-server", "sh", "-c",
                                        "getent hosts rag-site-test; curl -s -o /dev/null -w 'HTTP %{http_code}' http://rag-site-test/sitemap.xml"))
cfg = {"sitemap_url": "http://rag-site-test/sitemap.xml", "url_filter": "", "follow_pdf_links": False,
       "restrict_pdf_to_domain": True, "sync_deleted_files": False}
r = http("POST", "/connectors", json={"name": "Site Vélanor (test)", "source": "sitemap", "config": cfg, "refresh_freq": 30})
log(f"création du connecteur : {json.dumps(r, ensure_ascii=False)[:300]}")
cid = (r.get("data") or {}).get("id")
if cid:
    log(f"test du connecteur : {json.dumps(http('POST', f'/connectors/{cid}/test', json={}), ensure_ascii=False)[:400]}")
    rag = client()
    for d in rag.list_datasets(name="Essai-sitemap"):
        rag.delete_datasets(ids=[d.id])
    ds = rag.create_dataset(name="Essai-sitemap")
    r = http("PUT", f"/datasets/{ds.id}", json={"connectors": [{"id": cid, "auto_parse": "1"}]})
    log(f"liaison à la base : {json.dumps(r, ensure_ascii=False)[:200]}")
    time.sleep(40)
    log(f"journaux de synchronisation : {json.dumps(http('GET', f'/connectors/{cid}/logs'), ensure_ascii=False)[:800]}")
    log(f"documents de la base après 40 s : {[(d['name'], d.get('chunk_count')) for d in documents(ds.id)]}")
    rag.delete_datasets(ids=[ds.id])
    log(f"suppression du connecteur : {http('DELETE', f'/connectors/{cid}', json={})}")
journal = sh("docker", "logs", "--since", "2m", "rag-ragflow-server")
log("journal du serveur (lignes sitemap/connector/ssrf) :\n" + "\n".join(
    "  " + l[:300] for l in journal.splitlines() if any(k in l.lower() for k in ("sitemap", "connector", "non-public", "ssrf")))[-2500:])
sh("docker", "rm", "-f", "rag-site-test")
log("site de test supprimé")
(RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-sitemap.log").write_text("\n".join(lignes) + "\n")
