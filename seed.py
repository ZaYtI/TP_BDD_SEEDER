import psycopg2
from faker import Faker
import random
import getpass
import os
from dotenv import load_dotenv
import json


#Load JSON field in constant
with open('city.json', 'r') as fichier:
    CITY = json.load(fichier)

with open('activity.json', 'r') as fichier:
    ACTIVITY = json.load(fichier)

with open('activity.json', 'r') as fichier:
    CHALLENGE = json.load(fichier)

with open('team.json', 'r') as fichier:
    TEAM = json.load(fichier)



class DatabaseConnection:
    def __init__(self, database, username, server, password, port):
        self.database = database
        self.username = username
        self.server = server
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(
                database=self.database,
                user=self.username,
                host=self.server,
                password=self.password,
                port=self.port
            )
        return self.conn

    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

class BaseTable:
    def __init__(self, db_conn):
        self.conn = db_conn
        self.cur = self.conn.cursor()
        self.fake = Faker()

    def create(self, table_name, attributes):
        columns = ', '.join(attributes.keys())
        placeholders = ', '.join(['%s'] * len(attributes))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        self.cur.execute(query, list(attributes.values()))
        self.conn.commit()

    def delete_all(self, table_name):
        query = f"DELETE FROM {table_name};"
        self.cur.execute(query)
        self.conn.commit()

    def close(self):
        self.cur.close()

    def get_list_of_id_in_table(self, table_name):
        query = f"SELECT id FROM {table_name};"
        self.cur.execute(query)
        ids = self.cur.fetchall()
        return [row[0] for row in ids]

class Activite(BaseTable):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        city = random.choice(CITY)
        activity = random.choice(ACTIVITY)
        self.table_name = "Activite"
        self.attributes = {
            "Nom": activity['name'],
            "date_activite": self.fake.date_this_century(False,True),
            "lieu": city["nom"],
            "duree": random.randint(1,120),
            "descriptif": self.fake.text(),
            "nb_points": random.randint(0,1000),
            "nb_max": random.randint(0,1000)
        }
        CITY.remove(city)
        ACTIVITY.remove(activity)
        self.create(self.table_name, self.attributes)

class Equipe(BaseTable):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        team = random.choice(TEAM)
        self.table_name = "Equipe"
        self.attributes = {
            "nom": team['name'],
            "slogan": self.fake.catch_phrase(),
            "nb_points": random.randint(0,1000)
        }
        self.create(self.table_name, self.attributes)

class Etudiant(BaseTable):
    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.table_name = "Etudiant"
        self.attributes = {
            "nom":self.fake.last_name(),
            "prenom":self.fake.first_name(),
            "adresse":self.fake.address(),
            "nb_points": random.randint(0,1000),
            "id_formation": random.choice(self.get_list_of_id_in_table('Formation')),
            "id_equipe": random.choice(self.get_list_of_id_in_table('Equipe'))
        }
        self.create(self.table_name, self.attributes)

class Formation(BaseTable):
    def __init__(self,db_conn):
        super().__init__(db_conn)
        self.table_name = "Formation"
        self.attributes = {
            "diplome" : random.choice(['Licence', 'Master', 'Doctorat', 'Diplôme', 'Certificat']),
            "annee" : self.fake.year(),
            "departement" : self.fake.country()
        }
        self.create(self.table_name,self.attributes)

class Challenge(BaseTable):
    
    def __init__(self,db_conn):
        super().__init__(db_conn)
        self.table_name = "Challenge"
        challenge = random.choice(CHALLENGE)
        self.attributes = {
            "nom": f"Challenge : {challenge["name"]}",
            "date_challenge": self.fake.date(),
            "lieu":self.fake.country(),
            "duree":random.randint(1,120),
            "descriptif":self.fake.text()
        }
        ACTIVITY.remove(challenge)
        self.create(self.table_name,self.attributes)

class InscriptionActivite(BaseTable):

    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.table_name = "InscriptionActivite"
        self.attributes = {
            "id_activite": random.choice(self.get_list_of_id_in_table('Activite')),
            "id_etudiant":random.choice(self.get_list_of_id_in_table('Etudiant')),
        }
        self.create(self.table_name,self.attributes)

class InscriptionChallenge(BaseTable):

    def __init__(self, db_conn):
        super().__init__(db_conn)
        self.table_name = "InscriptionChallenge"
        self.attributes = {
            "id_challenge": random.choice(self.get_list_of_id_in_table('Challenge')),
            "id_equipe":random.choice(self.get_list_of_id_in_table('Equipe')),
        }
        self.create(self.table_name,self.attributes)

def main():  
    load_dotenv()

    DATABASE, USERNAME, SERVER, PASSWORD, PORT = get_database_credentials()
    
    
    db_conn = DatabaseConnection(DATABASE, USERNAME, SERVER, PASSWORD, PORT).connect()
    
    first_menu_choice(db_conn)

def first_menu_choice(db_conn):
    SEPARATOR = '/////////////////////////////////////////////////////'
    display_initial_menu(SEPARATOR)

    choice = int(input("Entrer votre choix :"))
    
    if choice == 1:
        row_number = int(input("Combien de tuples voulez-vous insérer dans chaque table : "))
        insert_in_all_table(row_number, db_conn)
    elif (choice == 2):
        table_classes = get_table_classes()
        handle_table_selection(table_classes, db_conn)
    elif (choice == 3):
        delete_data_for_all_table(db_conn)
    else:
        print('Erreur sélectionner un nombre présent dans les choix possible!!')
        first_menu_choice(db_conn)

def get_database_credentials():
    DATABASE = os.getenv('DATABASE') or input("Entrer le nom de votre base de donnée : ")
    USER = os.getenv('USERNAME') or input('Entrer le nom utilisateur : ')
    SERVER = os.getenv('SERVER') or input('Entrer le serveur : ')
    PASSWORD = os.getenv('PASSWORD') or getpass.getpass('Entrer le mot de passe : ')
    PORT = int(os.getenv('PORT')) or int(input('Entrer le port : '))
    return DATABASE, USER, SERVER, PASSWORD, PORT

def display_initial_menu(separator):
    print('\n')
    print(separator)
    print(separator)
    print('\n')
    print('1. Ajouter des données dans toutes les tables')
    print('2. Ajouter des données en sélectionnant les tables')
    print('3. Supprimer tout les enregistrement de tout les tables')
    print('\n')
    print(separator)
    print(separator)
    print('\n')

def get_table_classes():
    return {
        1: Activite,
        2: Equipe,
        3: Etudiant,
        4: Formation,
        5: Challenge,
        6: InscriptionActivite,
        7: InscriptionChallenge
    }

def handle_table_selection(table_classes, db_conn):
    while True:
        display_table_selection_menu()
        table_choice = int(input("Entrer le numéro de la table : "))

        if table_choice == 8:
            break

        row_number = int(input("Entrer le nombre de tuples voulus : "))

        if row_number != 0 and table_choice in table_classes:
            for _ in range(row_number):
                table_classes[table_choice](db_conn)

def display_table_selection_menu():
    SEPARATOR = '/////////////////////////////////////////////////////'
    print('\n')
    print(SEPARATOR)
    print(SEPARATOR)
    print('\n')
    print("Choisissez les tables dans lesquelles vous voulez ajouter des données : ")
    print("1. Activite")
    print("2. Equipe")
    print("3. Etudiant")
    print("4. Formation")
    print("5. Challenge")
    print("6. InscriptionActivite")
    print("7. InscriptionChallenge")
    print("8. Quitter")
    print('\n')
    print(SEPARATOR)
    print(SEPARATOR)
    print('\n')

def insert_in_all_table(row_number,db_conn):
    for _ in range(row_number):
        Formation(db_conn)
        Equipe(db_conn)
        Activite(db_conn)
        Challenge(db_conn)
    
    for _ in range(row_number):
        Etudiant(db_conn)
        InscriptionActivite(db_conn)
        InscriptionChallenge(db_conn)

def delete_data_for_all_table(db_conn):
    tables=["etudiant","inscription_activite","inscription_challenge","activite","equipe","formation","challenge"]
    cur = db_conn.cursor()
    for i in tables:
        query = f"DELETE FROM {i};"
        cur.execute(query)
        reset_increment = f"TRUNCATE TABLE {i} RESTART IDENTITY CASCADE"
        cur.execute(reset_increment)
    db_conn.commit()
    cur.close()

if __name__ == "__main__":
    main()
