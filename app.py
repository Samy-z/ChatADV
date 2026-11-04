"""Assistante Ventes — petite application locale, page web sur la machine.

Tout reste sur le PC: aucun service externe, aucun compte, aucune télémétrie.
Le modèle de langue tourne via Ollama en local (http://localhost:11434) et
n'est utilisé QUE pour les tâches de langue (traduire, rédiger). La recherche
de commandes lit le fichier CSV directement, sans modèle: un chiffre sorti
d'un tableau n'a pas à passer par une IA.

    python app.py            puis ouvrir http://localhost:8742

Le modèle par défaut est provisoire; la campagne de comparaison
(a-prime, docs/compare/campaign-assistante.md) désignera le gagnant.
"""

from __future__ import annotations

import csv
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = 8742
OLLAMA = os.environ.get("ASSISTANTE_OLLAMA", "http://localhost:11434")
MODELE = os.environ.get("ASSISTANTE_MODELE", "qwen3.5:4b")  # provisoire
FICHIER_COMMANDES = Path(os.environ.get("ASSISTANTE_COMMANDES",
                                        HERE / "data" / "exemple-commandes.csv"))

PROMPT_TRADUIRE = (
    "Tu es l'assistante d'une société française de pièces aéronautiques. "
    "Traduis fidèlement le message client suivant en français professionnel. "
    "Ne commente pas, n'ajoute rien, donne seulement la traduction.\n\n"
    "Message:\n{texte}")

PROMPT_REDIGER = (
    "Tu es l'assistante des ventes d'une société française de pièces "
    "aéronautiques. Rédige un e-mail professionnel, poli et concis "
    "({langue}) selon la consigne. Donne uniquement l'e-mail, avec un objet "
    "sur la première ligne.\n\nConsigne:\n{consigne}")


def appeler_ollama(prompt: str) -> tuple[bool, str]:
    """(ok, texte). Jamais d'exception vers l'interface: un message clair."""
    corps = json.dumps({"model": MODELE, "prompt": prompt, "stream": False,
                        "options": {"temperature": 0.2, "num_gpu": 0}})
    req = urllib.request.Request(OLLAMA + "/api/generate",
                                 data=corps.encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return True, json.loads(r.read().decode())["response"].strip()
    except Exception as e:  # noqa: BLE001
        return False, ("Le modèle local ne répond pas. Vérifiez qu'Ollama "
                       f"est démarré, puis réessayez. Détail: {e}")


def chercher_commande(numero: str) -> dict | None:
    if not FICHIER_COMMANDES.exists():
        return None
    with FICHIER_COMMANDES.open(encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if ligne.get("order_id", "").strip().lower() == numero.strip().lower():
                return ligne
    return None


class Handler(BaseHTTPRequestHandler):
    def _repondre(self, code: int, contenu: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(contenu)))
        self.end_headers()
        self.wfile.write(contenu)

    def _json(self, objet: dict, code: int = 200) -> None:
        self._repondre(code, json.dumps(objet, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            page = (HERE / "static" / "index.html").read_bytes()
            self._repondre(200, page, "text/html; charset=utf-8")
        else:
            self._repondre(404, b"introuvable", "text/plain")

    def do_POST(self):  # noqa: N802
        longueur = int(self.headers.get("Content-Length", 0))
        try:
            donnees = json.loads(self.rfile.read(longueur) or b"{}")
        except ValueError:
            self._json({"ok": False, "texte": "Requête illisible."}, 400)
            return
        if self.path == "/api/traduire":
            ok, texte = appeler_ollama(
                PROMPT_TRADUIRE.format(texte=donnees.get("texte", "")))
            self._json({"ok": ok, "texte": texte})
        elif self.path == "/api/rediger":
            langue = donnees.get("langue") or "en français"
            ok, texte = appeler_ollama(
                PROMPT_REDIGER.format(consigne=donnees.get("consigne", ""),
                                      langue=langue))
            self._json({"ok": ok, "texte": texte})
        elif self.path == "/api/commande":
            ligne = chercher_commande(donnees.get("numero", ""))
            if ligne is None:
                self._json({"ok": False,
                            "texte": "Commande introuvable dans le fichier."})
            else:
                self._json({"ok": True, "commande": ligne})
        else:
            self._json({"ok": False, "texte": "Action inconnue."}, 404)

    def log_message(self, *args):  # silencieux: rien ne quitte la machine
        pass


if __name__ == "__main__":
    print(f"Assistante Ventes — http://localhost:{PORT}")
    print(f"Modèle (provisoire): {MODELE} via {OLLAMA}")
    print(f"Fichier commandes: {FICHIER_COMMANDES}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
