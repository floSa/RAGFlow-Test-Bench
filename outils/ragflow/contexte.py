"""Change le contexte déclaré (max_tokens) du modèle de chat dans RAGFlow, puis l'affiche.

RAGFlow borne la réponse à « contexte déclaré − jetons du prompt » ; ce réglage sert aux essais de contexte serré
(banc) et de dépassement volontaire. Valeur de référence de la série : 16384.
Usage : uv run python outils/ragflow/contexte.py <max_tokens>
Journal : outils/resultats/ragflow/contexte-<date>.log
"""
import datetime, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import RACINE, http  # noqa: E402

n = int(sys.argv[1])
chemin = "/providers/OpenAI-API-Compatible/instances/llm-central/models"
avant = [m for m in http("GET", chemin)["data"] if m.get("name") == "chat"]
r = http("PATCH", f"{chemin}/chat", json={"max_tokens": n})
apres = [m for m in http("GET", chemin)["data"] if m.get("name") == "chat"]
lignes = [f"== {datetime.datetime.now().isoformat(timespec='seconds')} contexte déclaré -> {n}",
          f"avant : {json.dumps(avant, ensure_ascii=False)[:400]}",
          f"PATCH : {json.dumps(r, ensure_ascii=False)[:300]}",
          f"après : {json.dumps(apres, ensure_ascii=False)[:400]}"]
print("\n".join(lignes))
with (RACINE / f"outils/resultats/ragflow/contexte-{datetime.date.today()}.log").open("a") as f:
    f.write("\n".join(lignes) + "\n")
