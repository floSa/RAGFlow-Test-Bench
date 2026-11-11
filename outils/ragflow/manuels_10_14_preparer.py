"""Préparation, côté WSL, des captures des manuels 11, 12 et 14 (lot 4) ; les captures elles-mêmes sont faites à la
souris par outils/ragflow/captures/manuels_10_14.py.

  ingestion  : recette d'ingestion quotidienne (manuel 11) rejouée sur trois « jours » dans la base « Manuel-Ingestion »,
               par la fonction ingerer() de recette_ingestion.py ; journal 11-recettes/ingestion.log
  assistant  : assistant « Manuel-Reglages » relié à « Démo Vélanor » (réglages conseillés : Top N 8, poids des vecteurs
               0,7, invite par défaut), puis questions sans réponse dans le corpus posées par l'API pour choisir celle
               qui donne la réponse « not found » ; journal 14-depannage/preparation.log
Objets « Manuel-… » supprimés ensuite par outils/ragflow/nettoyer_manuel.py.
Usage : uv run python outils/ragflow/manuels_10_14_preparer.py <ingestion|assistant>
"""
import datetime, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, client, demander, documents  # noqa: E402
from recette_ingestion import ingerer  # noqa: E402

TXT = RACINE / "outils/resultats/ragflow/captures"


def journal(chemin, lignes):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("a") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes))


def ingestion():
    lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} recette d'ingestion, base Manuel-Ingestion"]
    dossier = RACINE / "donnees/manuel-depot"
    shutil.rmtree(dossier, ignore_errors=True); dossier.mkdir(parents=True)
    for jour, fichiers in (("jour 1", ["cse-2025-10-14.md", "faq-sav.html"]), ("jour 2", []),
                           ("jour 3", ["procedure-batteries.docx"])):
        for f in fichiers:
            shutil.copy(RACINE / "corpus/documents" / f, dossier)
        ds, ajout, duree = ingerer(dossier, "Manuel-Ingestion")
        lignes.append(f"{jour} : {len(ajout)} fichier(s) ajouté(s) en {duree:.0f} s {ajout} ; "
                      f"base : {len(documents(ds.id))} document(s)")
    shutil.rmtree(dossier)
    journal(TXT / "11-recettes/ingestion.log", lignes)


def assistant():
    rag = client()
    lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} assistant Manuel-Reglages"]
    for c in rag.list_chats(name="Manuel-Reglages"):
        rag.delete_chats(ids=[c.id])
    ds = rag.list_datasets(name="Démo Vélanor")[0]
    chat = rag.create_chat(name="Manuel-Reglages", dataset_ids=[ds.id], top_n=8, vector_similarity_weight=0.7)
    pc = chat.prompt_config.to_json()
    lignes.append(f"créé : top_n 8, poids des vecteurs 0,7 ; réponse vide {pc.get('empty_response')!r}")
    for q in ("Quelle est la capitale de l'Australie ?", "Quel est le numéro de TVA intracommunautaire de Vélanor ?"):
        s = chat.create_session("essai")
        r, d = demander(chat.id, s.id, q)
        lignes.append(f"question {q!r} ({d:.1f} s) : {((r.get('data') or {}).get('answer') or r)!r}"[:600])
    journal(TXT / "14-depannage/preparation.log", lignes)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
