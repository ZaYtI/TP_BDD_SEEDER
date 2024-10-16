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
    for table in tables:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
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
    data = []
    for i in tqdm(range(1, row_number + 1), desc="Insertion des challenges", unit="challenge"):
        nb_equipe = random.randint(1, 10)
        list_of_id_equipe = random.sample(id_equipe, nb_equipe)
        for j in list_of_id_equipe:
            data.append({"id_challenge": i, "id_equipe": j})
    create_batch(conn, "inscription_challenge", data)

def insert_inscription_activite(conn, row_number):
    id_etudiant = get_list_of_ids(conn, 'Etudiant', 'id_etudiant')
    data = []
    for i in tqdm(range(1, row_number + 1), desc="Insertion des activités", unit="activité"):
        nb_etu = random.randint(1, 10)
        list_of_id_etu = random.sample(id_etudiant, nb_etu)
        for j in list_of_id_etu:
            data.append({"id_activite": i, "id_etudiant": j})
    create_batch(conn, "inscription_activite", data)

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

def get_database_credentials():
    DATABASE = os.getenv('DATABASE') or input("Entrer le nom de votre base de donnée : ")
    USER = os.getenv('USERNAME') or input('Entrer le nom utilisateur : ')
    SERVER = os.getenv('SERVER') or input('Entrer le serveur : ')
    PASSWORD = os.getenv('PASSWORD') or getpass.getpass('Entrer le mot de passe : ')
    PORT = int(os.getenv('PORT')) or int(input('Entrer le port : '))
    return DATABASE, USER, SERVER, PASSWORD, PORT

def main_menu(conn):
    SEPARATOR = '/////////////////////////////////////////////////////'
    print(f"\n{SEPARATOR}\n{SEPARATOR}\n")
    print('1. Ajouter des données dans toutes les tables')
    print('2. Supprimer tous les enregistrements de toutes les tables')
    print('\n' + SEPARATOR + '\n' + SEPARATOR + '\n')

    choice = int(input("Entrer votre choix :"))

    if choice == 1:
        row_number = int(input("Combien de tuples voulez-vous insérer dans chaque table : "))
        insert_in_all_tables(conn, row_number)
    elif choice == 2:
        delete_all_data(conn)
        print("Toutes les données ont été supprimées.")
    else:
        print('Erreur, sélectionner un nombre présent dans les choix possibles!')
        main_menu(conn)

if __name__ == "__main__":
    load_dotenv()
    DATABASE, USERNAME, SERVER, PASSWORD, PORT = get_database_credentials()
    conn = connect_to_database(DATABASE, USERNAME, SERVER, PASSWORD, PORT)
    
    try:
        main_menu(conn)
    finally:
        close_connection(conn)
