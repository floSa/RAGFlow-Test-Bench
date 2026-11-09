"""Dépassement volontaire du contexte : contexte déclaré réduit, une question qui ramène beaucoup de passages.

Utilise le dataset « Banc-general » (créé par outils/ragflow/banc.py). Remet le contexte à 16384 à la fin.
Usage : uv run python outils/ragflow/essai_contexte.py [contexte=512] [top_n=12]
Sortie : outils/resultats/ragflow/essai-<date>-contexte-depassement.log
"""
import datetime, json, subprocess, sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from client import RACINE, client, demander  # noqa: E402

ctx = int(sys.argv[1]) if len(sys.argv) > 1 else 512
top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
out = RACINE / f"outils/resultats/ragflow/essai-{datetime.date.today()}-contexte-depassement.log"
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} contexte déclaré {ctx}, top_n {top_n}"]
rag = client()
ds = rag.list_datasets(name="Banc-general")[0]
subprocess.run(["uv", "run", "python", str(ICI / "contexte.py"), str(ctx)], check=True, capture_output=True)
for c in rag.list_chats(name="Essai-contexte"):
    rag.delete_chats(ids=[c.id])
chat = rag.create_chat(name="Essai-contexte", dataset_ids=[ds.id], top_n=top_n)
try:
    for q in ["Résume le rapport annuel 2025 de Vélanor : chiffre d'affaires, effectifs, sites et fournisseurs.",
              "Quel est le prix public du Vilaine Compact ?"]:
        sess = chat.create_session("ctx")
        r, d = demander(chat.id, sess.id, q)
        data = r.get("data") or {}
        lignes += [f"question : {q}", f"  durée {d:.1f} s ; code {r.get('code')} ; message {r.get('message')!r}",
                   f"  réponse : {str(data.get('answer'))[:400]!r}",
                   f"  passages cités : {len((data.get('reference') or {}).get('chunks') or [])}"]
finally:
    rag.delete_chats(ids=[chat.id])
    subprocess.run(["uv", "run", "python", str(ICI / "contexte.py"), "16384"], check=True, capture_output=True)
    lignes.append("contexte remis à 16384")
journal = subprocess.run(["docker", "logs", "--since", "3m", "rag-ragflow-server"], capture_output=True, text=True)
lignes += ["journal du serveur (lignes error/warn récentes) :"] + [
    "  " + l[:300] for l in (journal.stdout + journal.stderr).splitlines() if ("error" in l or "warn" in l) and "Admin server" not in l][-8:]
print("\n".join(lignes))
with out.open("a") as f:
    f.write("\n".join(lignes) + "\n")
