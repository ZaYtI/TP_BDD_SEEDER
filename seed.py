import psycopg2
from faker import Faker
import random
import getpass
import os
from dotenv import load_dotenv
from tqdm import tqdm

fake = Faker()

def connect_to_database(database, username, server, password, port):
    conn = psycopg2.connect(
        database=database,
        user=username,
        host=server,
        password=password,
        port=port
    )
    return conn

def close_connection(conn):
    if conn:
        conn.close()

def create_batch(conn, table_name, attributes_list):
    if not attributes_list:
        return
    cur = conn.cursor()
    columns = ', '.join(attributes_list[0].keys())
    placeholders = ', '.join(['%s'] * len(attributes_list[0]))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
    data = [tuple(attr.values()) for attr in attributes_list]
    cur.executemany(query, data)
    conn.commit()
    cur.close()

def delete_all_data(conn):
    tables = ["etudiant", "inscription_activite", "inscription_challenge", "activite", "equipe", "formation", "challenge"]
    cur = conn.cursor()
    for table in tqdm(tables, desc="Suppression des données", unit="table"):
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()

def delete_inscription_data(conn):
    tables = ["inscription_activite", "inscription_challenge"]
    cur = conn.cursor()
    for table in tqdm(tables, desc="Suppression des inscriptions", unit="table"):
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY;")
    conn.commit()
    cur.close()

def get_list_of_ids(conn, table_name, id_column_name):
    cur = conn.cursor()
    query = f"SELECT {id_column_name} FROM {table_name};"
    cur.execute(query)
    ids = cur.fetchall()
    cur.close()
    return [row[0] for row in ids]

def generate_formation_data(row_number):
    return [{
        "diplome": random.choice(['Licence', 'Master', 'Doctorat', 'Diplôme', 'Certificat']),
        "annee": fake.year(),
        "departement": fake.country()
    } for _ in range(row_number)]

def generate_equipe_data(row_number):
    return [{
        "nom": f'{fake.city_prefix()} {fake.first_name()}',
        "slogan": fake.catch_phrase(),
        "nb_points": random.randint(0, 1000)
    } for _ in range(row_number)]

def generate_activite_data(row_number):
    return [{
        "Nom": f'{fake.first_name()} {fake.city_suffix()}',
        "date_activite": fake.date_this_century(False, True),
        "lieu": fake.city(),
        "duree": random.randint(1, 120),
        "descriptif": fake.text(),
        "nb_points": random.randint(0, 1000),
        "nb_max": random.randint(0, 1000)
    } for _ in range(row_number)]

def generate_challenge_data(row_number):
    return [{
        "nom": f"Challenge : {fake.prefix()} {fake.city_suffix()}",
        "date_challenge": fake.date(),
        "lieu": fake.country(),
        "duree": random.randint(1, 120),
        "descriptif": fake.text()
    } for _ in range(row_number)]

def generate_etudiant_data(conn, row_number):
    id_formation = get_list_of_ids(conn, 'Formation', 'id_formation')
    id_equipe = get_list_of_ids(conn, 'Equipe', 'id_equipe')

    return [{
        "nom": fake.last_name(),
        "prenom": fake.first_name(),
        "adresse": fake.address(),
        "nb_points": random.randint(0, 1000),
        "id_formation": random.choice(id_formation),
        "id_equipe": random.choice(id_equipe)
    } for _ in range(row_number)]

def insert_inscription_challenge(conn, row_number):
    id_equipe = get_list_of_ids(conn, 'Equipe', 'id_equipe')
    id_challenge = get_list_of_ids(conn, 'Challenge', 'id_challenge')
    
    if len(id_challenge) == 0:
        print("Aucun challenge n'existe dans la table 'Challenge'.")
        return
    if len(id_equipe) == 0:
        print("Aucune équipe n'existe dans la table 'Equipe'.")
        return

    data = []
    delete_inscription_data(conn)
    existing_pairs = set()
    insert_row = 0
    
    for _ in tqdm(range(row_number), desc="Insertion des inscriptions challenge", unit="inscription"):
        challenge_id = random.choice(id_challenge)
        nb_equipes = random.randint(1, len(id_equipe))
        list_of_id_equipe = random.sample(id_equipe, nb_equipes)

        for equipe_id in list_of_id_equipe:
            pair = (challenge_id, equipe_id)

            if pair not in existing_pairs:
                data.append({"id_challenge": challenge_id, "id_equipe": equipe_id})
                existing_pairs.add(pair)
                insert_row+=1
        if(insert_row >= row_number):
            break
    
    if data:
        create_batch(conn, "inscription_challenge", data)
        print("Insertion des inscriptions dans 'inscription_challenge' terminée avec succès.")
    else:
        print("Aucune inscription unique à insérer.")



def insert_inscription_activite(conn, row_number):
    id_etudiant = get_list_of_ids(conn, 'Etudiant', 'id_etudiant')
    id_activite = get_list_of_ids(conn, 'Activite', 'id_activite')
    
    if len(id_activite) == 0:
        print("Aucune activité n'existe dans la table 'Activite'.")
        return
    if len(id_etudiant) == 0:
        print("Aucun étudiant n'existe dans la table 'Etudiant'.")
        return

    data = []
    delete_inscription_data(conn)
    existing_pairs = set()  
    insert_row = 0  

    for _ in tqdm(range(row_number), desc="Insertion des inscriptions activité", unit="inscription"):
        activity_id = random.choice(id_activite)
        nb_etudiants = random.randint(1, len(id_etudiant))
        list_of_id_etudiant = random.sample(id_etudiant, nb_etudiants)

        for etudiant_id in list_of_id_etudiant:
            pair = (activity_id, etudiant_id)

            if pair not in existing_pairs:  
                data.append({"id_activite": activity_id, "id_etudiant": etudiant_id})
                existing_pairs.add(pair)  
                insert_row += 1  
                
            if insert_row >= row_number:  
                break
        if insert_row >= row_number:  
            break

    if data:  
        create_batch(conn, "inscription_activite", data)
        print("Insertion des inscriptions dans 'inscription_activite' terminée avec succès.")
    else:
        print("Aucune inscription unique à insérer.")


def insert_in_all_tables(conn, row_number):
    print("Insertion dans Formation, Equipe, Activite, Challenge...")

    data_formations = generate_formation_data(row_number)
    data_equipes = generate_equipe_data(row_number)
    data_activites = generate_activite_data(row_number)
    data_challenges = generate_challenge_data(row_number)

    create_batch(conn, 'Formation', data_formations)
    create_batch(conn, 'Equipe', data_equipes)
    create_batch(conn, 'Activite', data_activites)
    create_batch(conn, 'Challenge', data_challenges)

    print("Insertion dans Etudiant...")
    data_etudiants = generate_etudiant_data(conn, row_number)
    create_batch(conn, 'Etudiant', data_etudiants)

    print("Insertion dans InscriptionChallenge...")
    insert_inscription_challenge(conn, row_number)

    print("Insertion dans InscriptionActivite...")
    insert_inscription_activite(conn, row_number)

def insert_in_single_table(conn, table_name, row_number):
    if table_name == 'Formation':
        data = generate_formation_data(row_number)
    elif table_name == 'Equipe':
        data = generate_equipe_data(row_number)
    elif table_name == 'Activite':
        data = generate_activite_data(row_number)
    elif table_name == 'Challenge':
        data = generate_challenge_data(row_number)
    elif table_name == 'Etudiant':
        data = generate_etudiant_data(conn, row_number)
    elif table_name == 'Inscription_Challenge':
        insert_inscription_challenge(conn, row_number)
        return
    elif table_name == 'Inscription_Activite':
        insert_inscription_activite(conn, row_number)
        return
    else:
        print("Table non valide.")
        return
    
    create_batch(conn, table_name, data)
    print(f"Insertion dans la table {table_name} terminée.")

def get_database_credentials():
    DATABASE = os.getenv('DATABASE') or input("Entrer le nom de votre base de donnée : ")
    USER = os.getenv('USERNAME') or input('Entrer le nom utilisateur : ')
    SERVER = os.getenv('SERVER') or input('Entrer le serveur : ')
    PASSWORD = os.getenv('PASSWORD') or getpass.getpass('Entrer le mot de passe : ')
    PORT = int(os.getenv('PORT')) or int(input('Entrer le port : '))
    return DATABASE, USER, SERVER, PASSWORD, PORT

def main_menu(conn):
    SEPARATOR = '/////////////////////////////////////////////////////'
    
    while True:  # Boucle principale du menu
        print(f"\n{SEPARATOR}\n{SEPARATOR}\n")
        print('1. Ajouter des données dans toutes les tables')
        print('2. Supprimer tous les enregistrements de toutes les tables')
        print('3. Ajouter des données dans une table spécifique')
        print('4. Quitter')
        print(f"\n{SEPARATOR}\n{SEPARATOR}\n")

        try:
            choice = int(input("Entrer votre choix :"))

            if choice == 1:
                row_number = int(input("Combien de tuples voulez-vous insérer dans chaque table : "))
                insert_in_all_tables(conn, row_number)
            elif choice == 2:
                delete_all_data(conn)
                print("Toutes les données ont été supprimées.")
            elif choice == 3:
                print("Liste des tables :")
                tables = ['Formation', 'Equipe', 'Activite', 'Challenge', 'Etudiant', 'Inscription_Challenge', 'Inscription_Activite']
                for i, table in enumerate(tables, 1):
                    print(f"{i}. {table}")
                table_choice = int(input("Sélectionnez un numéro de table : "))
                if 1 <= table_choice <= len(tables):
                    table_name = tables[table_choice - 1]
                    row_number = int(input(f"Combien de tuples voulez-vous insérer dans {table_name} : "))
                    insert_in_single_table(conn, table_name, row_number)
                else:
                    print("Numéro invalide.")
            elif choice == 4:
                print("Fermeture du programme.")
                break
            else:
                print("Erreur, sélectionner un nombre présent dans les choix possibles!")
        except ValueError:
            print("Entrée invalide, veuillez entrer un nombre.")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    load_dotenv()
    DATABASE, USERNAME, SERVER, PASSWORD, PORT = get_database_credentials()
    conn = connect_to_database(DATABASE, USERNAME, SERVER, PASSWORD, PORT)
    
    try:
        main_menu(conn)
    finally:
        close_connection(conn)
