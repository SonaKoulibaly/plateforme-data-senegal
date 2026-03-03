"""
run.py — Point d'entrée · Plateforme Data Sénégal
==================================================
Lance l'application Flask complète avec tous les dashboards.

Usage local :
    python run.py

Déploiement Render/Railway :
    gunicorn run:server --bind 0.0.0.0:$PORT
"""

import os
from flask_app import create_app

app    = create_app()
server = app  # Alias pour Gunicorn (run:server)

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 8090))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    print("\n" + "="*60)
    print("  🌍  PLATEFORME DATA SÉNÉGAL")
    print("="*60)
    print(f"  🏦  Bancaire    →  http://localhost:{port}/banque/")
    print(f"  ⚡  Énergie     →  http://localhost:{port}/energie/")
    print(f"  🛡  Assurance   →  http://localhost:{port}/assurance/")
    print(f"  🏥  Hospitalier →  http://localhost:{port}/hospitalier/")
    print(f"  🏠  Accueil     →  http://localhost:{port}/")
    print("="*60 + "\n")

    app.run(debug=debug, host="0.0.0.0", port=port)
    