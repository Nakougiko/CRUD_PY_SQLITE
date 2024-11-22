import sqlite3

# Connexion à la base de données (ou création si elle n'existe pas)
connexion = sqlite3.connect("database.db")
databaseC = connexion.cursor()

"""
-------------------
GESTION DES TABLES
-------------------
"""
def creer_tables():
    # Table groupes
    databaseC.execute("""
    CREATE TABLE IF NOT EXISTS groupes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    )
    """)

    # Table contacts
    databaseC.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT,
        date_naissance DATE,
        groupe_id INTEGER,
        FOREIGN KEY (groupe_id) REFERENCES groupes(id)
    )
    """)

    # Table téléphones
    databaseC.execute("""
    CREATE TABLE IF NOT EXISTS telephones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        type TEXT,
        numero TEXT NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    """)

    # Table interactions
    databaseC.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        type TEXT,
        date DATETIME,
        description TEXT,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    """)

    # Table emails
    databaseC.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER,
        type TEXT,
        email TEXT NOT NULL,
        FOREIGN KEY (contact_id) REFERENCES contacts(id)
    )
    """)

    # Sauvegarder les changements
    connexion.commit()

"""
-------------------
Fonction generique
-------------------
"""

# Inserer une donnée
def ajouter_donnee(table, donnees):
    colonnes = ", ".join(donnees.keys())
    valeurs_placeholders = ", ".join("?" for _ in donnees)
    valeurs = tuple(donnees.values())

    requete = f"INSERT INTO {table} ({colonnes}) VALUES ({valeurs_placeholders})"
    databaseC.execute(requete, valeurs)
    connexion.commit()

# Lire une donnée
def lire_donnee(table, conditions=None):
    if conditions:
        clause_conditions = " AND ".join(f"{col} = ?" for col in conditions)
        valeurs = tuple(conditions.values())
        requete = f"SELECT * FROM {table} WHERE {clause_conditions}"
        databaseC.execute(requete, valeurs)

    else:
        requete = f"SELECT * FROM {table}"
        databaseC.execute(requete)

    return databaseC.fetchall()

# Modifier une donnee
def maj_donnee(table, nouvelles_valeurs, conditions):
    set_clause = ", ".join(f"{col} = ?" for col in nouvelles_valeurs)
    where_clause = " AND ".join(f"{col} = ?" for col in conditions)

    valeurs = tuple(nouvelles_valeurs.values()) + tuple(conditions.values())
    requete = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    databaseC.execute(requete, valeurs)
    connexion.commit()

# Supprimer une donnee
def supprimer_donnee(table, conditions):
    where_clause = " AND ".join(f"{col} = ? " for col in conditions)
    valeurs = tuple(conditions.values())

    requete = f"DELETE FROM {table} WHERE {where_clause}"
    databaseC.execute(requete, valeurs)
    connexion.commit()


"""
------
Fonction utilitaire
------
"""
def recuperer_tables():
    # Requête pour récupérer toutes les tables
    databaseC.execute("SELECT name FROM sqlite_master WHERE type='table'")

    # Récupération des résultats
    tables = databaseC.fetchall()

    # Extraction des noms de tables depuis les résultats
    return [table[0] for table in tables if table[0] != "sqlite_sequence"]

def recuperer_colonnes(table):
    # Recuperer les colonnes de la table
    databaseC.execute(f"PRAGMA table_info({table})")
    colonnes = databaseC.fetchall()
    # exclure la colonne id
    return [colonne[1] for colonne in colonnes if colonne[1] != "id"]
"""
------
Partie utilisateur
------
"""

def action_utilisateur():
    print()
    print("1. Ajouter une donnée")
    print("2. Modifier une donnée")
    print("3. Supprimer une donnée")
    print("4. Consulter une donnée")
    choix = int(input("\nVeuillez choisir une action : "))
    return choix

def tables_selection():
    print("Tables dans la base de données : ", recuperer_tables())

    table_choisis = ""
    while table_choisis not in recuperer_tables():
        table_choisis = str(input("Veuillez choisir une table : "))
        if table_choisis not in recuperer_tables():
            print("La table choisis n'existe pas")
        else:
            return table_choisis

def saisir_donnees(table):
    colonnes = recuperer_colonnes(table)
    donnees = {}
    for colonne in colonnes:
        valeur = input(f"Veuillez entrer la valeur pour '{colonne}': ")
        donnees[colonne] = valeur
    return donnees

def saisir_conditions(table):
    colonnes = recuperer_colonnes(table)
    conditions = {}
    for colonne in colonnes:
        valeur = input(f"Veuillez entrer la valeur pour la condition sur '{colonne}' (laisser vide pour ignorer) : ")
        if valeur:
            conditions[colonne] = valeur
    return conditions

def saisir_nouvelles_valeurs(table):
    colonnes = recuperer_colonnes(table)
    nouvelles_valeurs = {}
    for colonne in colonnes:
        valeur = input(f"Veuillez entrer la nouvelle valeur pour '{colonne}' (laisser vide pour ignorer) : ")
        if valeur:
            nouvelles_valeurs[colonne] = valeur
    return nouvelles_valeurs

"""
-------
BOUCLE
-------
"""
creer_tables()
while True:
    choix = action_utilisateur()
    table_choisis = tables_selection()
    match choix:
        case 1:
            #Ajouter
            donnnes = saisir_donnees(table_choisis)
            ajouter_donnee(table_choisis, donnnes)
        case 2:
            #Modifier
            conditions = saisir_conditions(table_choisis)
            nouvelles_valeurs = saisir_nouvelles_valeurs(table_choisis)
            if conditions and nouvelles_valeurs:
                maj_donnee(table_choisis, nouvelles_valeurs, conditions)
        case 3:
            #Supprimer
            conditions = saisir_conditions(table_choisis)
            if conditions:
                supprimer_donnee(table_choisis, conditions)
        case 4:
            #Consulter
            conditions = saisir_conditions(table_choisis)
            resultats = lire_donnee(table_choisis, conditions)
            if resultats:
                for ligne in resultats:
                    print(ligne)
        case _:
            print("Choix invalide")

