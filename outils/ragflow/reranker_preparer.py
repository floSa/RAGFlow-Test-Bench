"""Préparation et contrôles, côté WSL, des captures du reranker (outils/ragflow/captures/reranker.py).

  base04   : base « Manuel-Prise-en-main » (deux fichiers du chapitre 04, analysés) pour refaire la capture du
             chapitre 04, étape 15 ; journal captures/02-prise-en-main/preparation-reranker.log
  appels   : appels /v1/rerank reçus par vllm-rerank depuis une date (journal du conteneur, filtré) ;
             usage : reranker_preparer.py appels <depuis, ex. 2026-11-11T21:00:00>
Objets « Manuel-… » supprimés ensuite par outils/ragflow/nettoyer_manuel.py.
Usage : uv run python outils/ragflow/reranker_preparer.py <base04|appels> [...]
"""
import datetime, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, attendre_analyse, client  # noqa: E402

TXT = RACINE / "outils/resultats/ragflow/captures"


def base04():
    rag = client()
    lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} base Manuel-Prise-en-main (chapitre 04, étape 15)"]
    for d in rag.list_datasets(name="Manuel-Prise-en-main"):
        rag.delete_datasets(ids=[d.id])
    ds = rag.create_dataset(name="Manuel-Prise-en-main")
    fichiers = [RACINE / "corpus/documents" / f for f in ("cse-2025-10-14.md", "faq-sav.html")]
    docs = ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()} for f in fichiers])
    ds.async_parse_documents([d.id for d in docs])
    etats, duree = attendre_analyse(ds.id, [d.id for d in docs], delai_max=600)
    lignes.append(f"analyse en {duree:.0f} s : {etats}")
    (TXT / "02-prise-en-main").mkdir(parents=True, exist_ok=True)
    with (TXT / "02-prise-en-main/preparation-reranker.log").open("a") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes))


def appels(depuis):
    out = subprocess.run(["docker", "logs", "--since", depuis, "vllm-rerank"], capture_output=True, text=True)
    lignes = [l for l in (out.stdout + out.stderr).splitlines() if "rerank" in l.lower() and "POST" in l]
    print(f"{len(lignes)} appel(s) POST …rerank reçus par vllm-rerank depuis {depuis}")
    print("\n".join(lignes[-20:]))


if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])
