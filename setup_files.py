import os

data = {
    "client_A": {
        "docA1.txt": "Procédure résiliation\nLa résiliation doit être enregistrée dans le CRM.\nUn accusé de réception est envoyé sous 48h.\nLe responsable conformité valide les dossiers sensibles.",
        "docA2.txt": "Produit RC Pro A\nLa RC Pro couvre les dommages causés aux tiers dans le cadre de l’activité déclarée.\nExclusion : travaux en hauteur au-delà de 3 mètres.\nDéclaration de sinistre : service sinistres@assureur-a.fr."
    },
    "client_B": {
        "docB1.txt": "Procédure sinistre\nTout sinistre doit être déclaré dans les 5 jours ouvrés.\nL’équipe gestion transmet le dossier au gestionnaire assureur.\nLe suivi du sinistre est effectué de manière hebdomadaire.",
        "docB2.txt": "Produit RC Pro B\nLa RC Pro couvre l’activité déclarée.\nExclusion : sous-traitance non déclarée.\nDéclaration de sinistre : claims@assureur-b.com."
    }
}

for client, docs in data.items():
    os.makedirs(f"data/{client}", exist_ok=True)
    for filename, content in docs.items():
        with open(f"data/{client}/{filename}", "w", encoding="utf-8") as f:
            f.write(content)

print("Dossiers et fichiers créés dans /data")