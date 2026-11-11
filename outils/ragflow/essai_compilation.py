"""Knowledge Compilation : carte mentale (mind_map) produite par un pipeline d'ingestion avec composant Compiler.

1. groupe de gabarits de compilation (gabarit intégré « mind_map ») ;
2. pipeline « general » + nœud Compiler entre Extractor et Tokenizer, créé puis publié ;
3. base d'essai en mode pipeline (parse_type=2), document court (compte rendu du CSE), ingestion ;
4. suivi de /compilation/status, lecture de l'artefact ; limite de 30 minutes (consigne du banc).
Usage : uv run python outils/ragflow/essai_compilation.py [kind=mind_map]
Sortie : outils/resultats/ragflow/essai-<date>-compilation-<kind>.log
"""
import datetime, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, documents, http  # noqa: E402

KIND = sys.argv[1] if len(sys.argv) > 1 else "mind_map"
ART = {"mind_map": "mindmap", "knowledge_graph": "graph", "timeline": "timeline"}.get(KIND, KIND)
LLM = "chat@llm-central@OpenAI-API-Compatible"
NOM = f"Essai-KC-{KIND}-{datetime.datetime.now():%H%M}"
SORTIE = RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-compilation-{KIND}.log"
T0 = datetime.datetime.now()
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} Knowledge Compilation, gabarit {KIND}"]


def log(m):
    print(m, flush=True)
    lignes.append(str(m))
    SORTIE.write_text("\n".join(lignes) + "\n")


def court(r, n=400):
    return json.dumps(r, ensure_ascii=False)[:n]


builtins = http("GET", "/compilation-templates/builtins")["data"]
gab = next(t for t in builtins if t.get("kind") == KIND)
r = http("POST", "/compilation-template-groups", json={"name": NOM, "templates": [
    {"name": gab.get("display_name", KIND), "kind": KIND, "config": gab.get("config")}]})
log(f"groupe de gabarits : {court(r, 250)}")
gid = (r.get("data") or {}).get("id")

dsl = http("GET", "/pipelines/general")["data"]
dsl = dsl.get("dsl", dsl)
c = dsl["components"]
ext = next(k for k in c if k.startswith("Extractor"))
tok = next(k for k in c if k.startswith("Tokenizer"))
comp = "Compiler:EssaiBanc"
c[comp] = {"obj": {"component_name": "Compiler", "params": {"compilation_template_group_id": gid, "llm_id": LLM,
                                                             "plan": False}},
           "upstream": [ext], "downstream": [tok]}
c[ext]["downstream"] = [comp]
c[tok]["upstream"] = [comp]
r = http("POST", "/agents", json={"title": NOM, "canvas_category": "dataflow_canvas", "dsl": dsl})
log(f"création du pipeline : {court(r, 250)}")
pid = (r.get("data") or {}).get("id") if isinstance(r.get("data"), dict) else None
r = http("POST", f"/agents/{pid}/publish", json={})
log(f"publication : {court(r, 250)}")
vid = (r.get("data") or {}).get("id") if isinstance(r.get("data"), dict) else None

rag = client()
for d in rag.list_datasets(name=NOM):
    rag.delete_datasets(ids=[d.id])
r = http("POST", "/datasets", json={"name": NOM, "parse_type": 2, "pipeline_id": pid, "pipeline_version_id": vid})
log(f"base en mode pipeline : {court(r, 250)}")
ds = rag.list_datasets(name=NOM)[0]
f = RACINE / "corpus/documents/cse-2025-10-14.md"
doc = ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()}])[0]
r = http("POST", f"/datasets/{ds.id}/documents/parse", json={"document_ids": [doc.id]})
log(f"ingestion lancée : {court(r, 200)}")
t0 = time.time()
etat = {}
while time.time() - t0 < 1800:
    d = documents(ds.id)[0]
    etat = http("GET", f"/datasets/{ds.id}/compilation/status", params={"kind": ART}).get("data")
    if int(time.time() - t0) % 60 < 6:
        log(f"  {time.time() - t0:5.0f} s : document progress={d.get('progress')} passages={d.get('chunk_count')} ; compilation {court(etat, 200)}")
    # l'état revient à « idle » une fois la compilation faite : la fin se lit à last_completed_at, file vide
    if isinstance(etat, dict) and (etat.get("error") or etat.get("state") in ("completed", "failed", "error") or (
            etat.get("last_completed_at") and not etat.get("backlog") and not etat.get("inflight")
            and float(d.get("progress") or 0) >= 1)):
        break
    time.sleep(5)
log(f"fin du suivi après {time.time() - t0:.0f} s ; état : {court(etat, 400)}")
art = http("GET", f"/datasets/{ds.id}/artifacts/structure", params={"kind": ART})
log(f"artefact {ART} : {court(art, 3000)}")
log(f"document : {court({k: documents(ds.id)[0].get(k) for k in ('progress', 'chunk_count', 'progress_msg')}, 600)}")
