from flask import Flask, render_template, url_for, abort
import os, re

app = Flask(__name__)  # static/ est utilisé par défaut comme dossier de fichiers statiques

CHAPITRES = [
   
    "chapitre0","chapitre1", "chapitre2", "chapitre3", "chapitre4",
    "chapitre5","chapitre6","chapitre7","chapitre8",
    "chapitre9","chapitre10", "chapitre11", "chapitre12",
    "chapitre13","chapitre14","chapitre15","chapitre16",
    "chapitre17","chapitre18","chapitre19","chapitre20",
    "chapitre21", "chapitre22", "chapitre23", "chapitre24",
    "chapitre25","chapitre26","chapitre27","chapitre28",
    "chapitre29","chapitre30", "chapitre31", "chapitre32",
    "chapitre33","chapitre34","chapitre35","chapitre36",
    "chapitre37","chapitre48","chapitre96","chapitre128",
    "chapitre256","chapitre512","chapitre1024","chapitre2048","chapitre3000","chapitre3001",
    "chapitre3302","chapitre3003","chapitre3004","chapitre3005","chapitre3006","chapitre3007","chapitre4000","chapitre4001","chapitre6000",
]

VALID_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# --- utils --------------------------------------------------------------------

_suffix_re = re.compile(r'^(?:[_\-])?([a-z])(\d+)$')  # _a1 / -b2 / a3

def _parse_variant(basename: str, nom: str):
    """
    basename = nom de fichier sans extension (p.ex. 'chapitre1_a2')
    nom = nom du chapitre (p.ex. 'chapitre1')
    Retourne:
      - ('a', 0, True) pour l’image principale (nom.jpg)
      - (letter, index_int, False) pour les variantes nom_a1, nom-b2, noma3, etc.
      - None si non conforme
    """
    if not basename.startswith(nom):
        return None
    rest = basename[len(nom):]  # '', '_a1', '-b2', 'a3'...
    if rest == "":
        return ("a", 0, True)  # image principale dans la colonne 'a' en tête
    m = _suffix_re.match(rest)
    if m:
        letter = m.group(1).lower()
        idx = int(m.group(2))
        return (letter, idx, False)
    # tenter le format sans séparateur (ex: 'a3' déjà géré plus haut, donc on tombe ici si autre chose)
    return None

def _collect_images(nom: str):
    """
    Balaye static/ et construit une liste de colonnes d’images.
    Chaque colonne = liste d’objets {url, alt}, dans l’ordre.
    """
    if not os.path.isdir(app.static_folder):
        return []

    variants = []  # (letter, idx, is_main, url)
    for fname in os.listdir(app.static_folder):
        root, ext = os.path.splitext(fname)
        if ext.lower() not in VALID_EXTS:
            continue
        parsed = _parse_variant(root, nom)
        if not parsed:
            continue
        letter, idx, is_main = parsed
        url = url_for("static", filename=fname)
        variants.append((letter, idx, is_main, url))

    if not variants:
        return []

    # trier : d’abord par lettre (a, b, c...), puis par index (0,1,2...)
    variants.sort(key=lambda t: (t[0], t[1]))

    # regrouper par lettre
    columns = {}
    for letter, idx, is_main, url in variants:
        columns.setdefault(letter, [])
        columns[letter].append({
            "url": url,
            "alt": f"Illustration {nom} - série {letter} #{idx}"
        })

    # on veut l’ordre a, b, c... (si 'a' n’existe pas, l’ordre naturel des clés)
    ordered_letters = sorted(columns.keys())
    return [columns[letter] for letter in ordered_letters]

# -----------------------------------------------------------------------------

@app.route("/")
def accueil():
    return render_template("index.html", chapitres=CHAPITRES)

@app.route("/chapitre/<nom>")
def afficher_chapitre(nom):
    # Sécurise: n'autorise que les chapitres connus
    if nom not in CHAPITRES:
        abort(404)

    # Fichier texte (placé à la racine du projet ou adapte le chemin si besoin)
    chemin_txt = os.path.join(os.getcwd(), f"{nom}.txt")
    try:
        with open(chemin_txt, "r", encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        contenu = "Chapitre introuvable."

    # Récupère les images par colonnes
    image_columns = _collect_images(nom)  # liste de listes (colonnes -> images empilées)

    return render_template(
        "chapitre.html",
        nom=nom,
        contenu=contenu,
        image_columns=image_columns,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



