"""DeepDoc et correction manuelle des passages, sur le contrat scanné (2 pages).

1. analyse seule du scan, chronométrée (temps par page) ;
2. lecture des passages ; recherche « volume minimal annuel 40 000 » avant correction ;
3. correction du texte OCR d'un passage (PATCH), puis même recherche ;
4. désactivation puis réactivation du passage ; ajout d'un passage manuel ;
5. suppression de la base d'essai.
Usage : uv run python outils/ragflow/essai_passages.py   Sortie : outils/resultats/ragflow/essai-<date>-passages.log
"""
import datetime, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, attendre_analyse, client, http  # noqa: E402

lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} essai DeepDoc et correction des passages"]


def log(m):
    print(m, flush=True)
    lignes.append(str(m))


def recherche(ds_id, q):
    r = http("POST", "/retrieval", json={"question": q, "dataset_ids": [ds_id], "similarity_threshold": 0.0, "top_k": 50,
                                         "page_size": 3})
    return [(round(c.get("similarity", 0), 3), c.get("content", "")[:90].replace("\n", " ")) for c in r["data"]["chunks"]]


rag = client()
for d in rag.list_datasets(name="Essai-passages"):
    rag.delete_datasets(ids=[d.id])
ds = rag.create_dataset(name="Essai-passages", parser_id="general")
f = RACINE / "corpus/documents/contrat-batterix-scan.pdf"
doc = ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()}])[0]
t = time.time()
ds.async_parse_documents([doc.id])
etats, _ = attendre_analyse(ds.id, [doc.id], pas=1)
duree = time.time() - t
log(f"analyse du scan (2 pages, 747 Ko) : {duree:.1f} s, soit {duree / 2:.1f} s par page ; {etats}")
base = f"/datasets/{ds.id}/documents/{doc.id}/chunks"
chunks = http("GET", base)["data"]["chunks"]
c = chunks[0]
log(f"passages : {len(chunks)} ; extrait OCR : {c['content'][:260]!r}")
q = "volume minimal annuel de 40 000 batteries"
log(f"recherche avant correction « {q} » : {recherche(ds.id, q)}")
corrige = (c["content"].replace("Volumeminimalannuel:40 0oo", "Volume minimal annuel : 40 000")
           .replace("debatteries48V", "de batteries 48 V").replace("1 0o0 cycles", "1 000 cycles"))
r = http("PATCH", f"{base}/{c['id']}", json={"content": corrige})
log(f"PATCH du passage (texte corrigé) : {r}")
time.sleep(2)
apres = http("GET", base)["data"]["chunks"][0]
log(f"texte relu après correction : {apres['content'][:260]!r}")
log(f"recherche après correction : {recherche(ds.id, q)}")
r = http("PATCH", base, json={"chunk_ids": [c["id"]], "available_int": 0})
time.sleep(2)
log(f"désactivation : {r} ; recherche : {recherche(ds.id, q)}")
r = http("PATCH", base, json={"chunk_ids": [c["id"]], "available_int": 1})
log(f"réactivation : {r}")
r = http("POST", base, json={"content": "Note manuelle : le contrat Batterix BX-2025-117 est suivi par le service achats.",
                              "important_keywords": ["achats", "Batterix"]})
log(f"ajout d'un passage manuel : code {r.get('code')} ; passages ensuite : {len(http('GET', base)['data']['chunks'])}")
rag.delete_datasets(ids=[ds.id])
log("base d'essai supprimée")
(RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-passages.log").write_text("\n".join(lignes) + "\n")
