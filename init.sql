DROP DATABASE IF EXISTS insa;

CREATE DATABASE insa;

USE insa;

DROP TABLE IF EXISTS InscriptionChallenge;
DROP TABLE IF EXISTS InscriptionActivite;
DROP TABLE IF EXISTS Challenge;
DROP TABLE IF EXISTS Activite;
DROP TABLE IF EXISTS Etudiant;
DROP TABLE IF EXISTS Equipe;
DROP TABLE IF EXISTS Formation;

CREATE TABLE formation (
    id_formation SERIAL PRIMARY KEY,
    diplome VARCHAR(255),
    annee INT,
    departement VARCHAR(255)
);

CREATE TABLE equipe (
    id_equipe SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    slogan VARCHAR(255),
    nb_points INT DEFAULT 0
);

CREATE TABLE etudiant (
    id_etudiant SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    adresse VARCHAR(255),
    nb_points INT DEFAULT 0,
    id_formation INT,
    id_equipe INT,
    FOREIGN KEY (id_formation) REFERENCES formation(id_formation) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE activite (
    id_activite SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    date_activite DATE,
    lieu VARCHAR(255),
    duree INT,
    descriptif TEXT,
    nb_points INT,
    nb_max INT
);

CREATE TABLE inscription_activite (
    id_activite INT,
    id_etudiant INT,
    PRIMARY KEY (id_activite, id_etudiant),
    FOREIGN KEY (id_activite) REFERENCES activite(id_activite) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_etudiant) REFERENCES etudiant(id_etudiant) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE challenge (
    id_challenge SERIAL PRIMARY KEY,
    nom VARCHAR(255),
    date_challenge DATE,
    lieu VARCHAR(255),
    duree INT,
    descriptif TEXT,
    nb_points INT,
    nb_equipes INT
);

CREATE TABLE inscription_challenge (
    id_challenge INT,
    id_equipe INT,
    PRIMARY KEY (id_challenge, id_equipe),
    FOREIGN KEY (id_challenge) REFERENCES challenge(id_challenge) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE CASCADE ON UPDATE CASCADE
);
