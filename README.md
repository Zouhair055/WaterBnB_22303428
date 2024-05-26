# Projet de Régulation de Piscine Connectée

## Table of Contents
1. [Introduction](#Introduction)
2. [Architecture du Système](#Architecture-du-Système)
3. [Fonctionnalités](#Fonctionnalités)
4. [Configuration](#Configuration)
5. [Team Members](#team-members)

# LINKS
https://github.com/Zouhair055/WaterBnB_22303428
https://waterbnb-22303428.onrender.com
https://charts.mongodb.com/charts-iot-kfcpuqu/public/dashboards/66534d64-4ae7-4514-88b6-12caaadfd11d

## Introduction
Ce projet développe un système de régulation de piscine intelligente utilisant MongoDB, MongoDB Charts, ESP et Node-RED. Il permet de surveiller et de gérer les paramètres de la piscine tels que la température, l'occupation et les hotspots, tout en gardant une trace des utilisateurs connectés.
1. Clone the repository:
    ```bash
    git clone git@github.com:Zouhair055/WaterBnB_22303428.git
    ```
  
3. Run the application.

## Architecture du Système
- #### MongoDB
Stocke les logs d'accès et les paramètres de la piscine sous forme de documents JSON.
 
- #### MongoDB Charts
Visualise les données stockées dans MongoDB avec divers graphiques.

- #### ESP (Embedded System Platform)
Collecte les données en temps réel des paramètres de la piscine et les envoie à MongoDB via Node-RED.

- #### Node-RED
Orchestre l'envoi des données des dispositifs ESP vers MongoDB, incluant l'identifiant client unique pour chaque utilisateur.



## Fonctionnalités
- #### Collecte des Données
Température : Mesurée par les dispositifs ESP.
Occupation : Détection de l'occupation de la piscine.
Hotspots : Détection de hotspots.
- #### Visualisation des Données
Graphique à barres empilées : Pools les plus utilisés.
Graphique circulaire (donut chart) : Répartition des températures.
Graphique de ligne discrète : Températures maximales par heure ou dans le temps.
- #### Gestion des Pools
Surveillance en temps réel des paramètres.
Analyse des données historiques avec MongoDB Charts.
Gestion des accès utilisateurs avec ID client unique via Node-RED.

## Configuration
- #### Connexion de l'ESP
Configurez l'ESP pour mesurer les paramètres de la piscine.
Programmez l'ESP pour envoyer les données à Node-RED.
- #### Configuration de Node-RED
Créez des flux pour recevoir les données des dispositifs ESP.
Formatez et envoyez les données à MongoDB avec un ID client unique.
![Capture d’écran 2024-05-26 185607](https://vu.fr/YehRG)

- #### Configuration de MongoDB et MongoDB Charts
Configurez MongoDB pour stocker les données.
Créez les visualisations nécessaires dans MongoDB Charts.
![Capture d’écran 2024-05-26 185724](https://vu.fr/SPbs)



## Team Members
The project was developed by the following team members:
- Zouhair DKHISSI
- Ayoub EL ALAMI EL FILALI





