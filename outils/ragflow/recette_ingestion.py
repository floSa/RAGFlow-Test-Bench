"""Recette : ingestion automatique d'un dossier dans une base RAGFlow, sans doublon (à lancer chaque jour par cron).

Importe les fichiers du dossier absents de la base (comparaison par nom), lance l'analyse, attend la fin.
Usage : uv run python outils/ragflow/recette_ingestion.py <dossier> <nom de la base>
Essai (sortie : outils/resultats/ragflow/essai-<date>-recette-ingestion.log) :
  uv run python outils/ragflow/recette_ingestion.py --essai
"""
import datetime, shutil, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, attendre_analyse, client, demander, documents  # noqa: E402


def ingerer(dossier, nom):
    rag = client()
    bases = rag.list_datasets(name=nom)
    ds = bases[0] if bases else rag.create_dataset(name=nom, parser_id="general")
    deja = {d["name"] for d in documents(ds.id)}
    nouveaux = sorted(f for f in Path(dossier).iterdir() if f.is_file() and f.name not in deja)
    if not nouveaux:
        return ds, [], 0.0
    docs = ds.upload_documents([{"display_name": f.name, "blob": f.read_bytes()} for f in nouveaux])
    ds.async_parse_documents([d.id for d in docs])
    etats, duree = attendre_analyse(ds.id, [d.id for d in docs])
    return ds, [(n, e["chunks"]) for n, e in etats.items()], duree


if __name__ == "__main__":
    if sys.argv[1:] != ["--essai"]:
        ds, ajout, duree = ingerer(sys.argv[1], sys.argv[2])
        print(f"{len(ajout)} fichier(s) ajouté(s) en {duree:.0f} s : {ajout}")
        sys.exit(0)
    lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} recette d'ingestion quotidienne"]
    dossier = RACINE / "donnees/recette-depot"
    shutil.rmtree(dossier, ignore_errors=True); dossier.mkdir(parents=True)
    rag = client()
    for d in rag.list_datasets(name="Recette-ingestion"):
        rag.delete_datasets(ids=[d.id])
    for jour, fichiers in (("jour 1", ["cse-2025-10-14.md", "faq-sav.html"]), ("jour 2", []), ("jour 3", ["procedure-batteries.docx"])):
        for f in fichiers:
            shutil.copy(RACINE / "corpus/documents" / f, dossier)
        ds, ajout, duree = ingerer(dossier, "Recette-ingestion")
        lignes.append(f"{jour} : {len(ajout)} fichier(s) ajouté(s) en {duree:.0f} s {ajout} ; base : {len(documents(ds.id))} document(s)")
    chat = rag.create_chat(name="Recette-ingestion", dataset_ids=[ds.id])
    s = chat.create_session("recette")
    r, d = demander(chat.id, s.id, "Où et à quelle température les batteries doivent-elles être stockées ?")
    lignes.append(f"question après le jour 3 ({d:.1f} s) : {r['data']['answer']}")
    rag.delete_chats(ids=[chat.id]); rag.delete_datasets(ids=[ds.id]); shutil.rmtree(dossier)
    lignes.append("base, assistant et dossier d'essai supprimés")
    print("\n".join(lignes))
    (RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-recette-ingestion.log").write_text("\n".join(lignes) + "\n")
