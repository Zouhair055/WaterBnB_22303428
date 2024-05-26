from flask import Flask, request, render_template
from pymongo import MongoClient
from bson import json_util
import os
import threading
import paho.mqtt.client as mqtt
import json
from datetime import datetime

app = Flask(__name__)

# Configuration de la connexion MongoDB
mongo_uri = "mongodb+srv://dkhissizouhair5:Youness123@cluster0.kpfpdda.mongodb.net/"
client = MongoClient(mongo_uri)
db = client['WaterBnb']
users_collection = db['users']
pools_collection = db['pool']
access_logs_collection = db['access_logs']  # Nouvelle collection pour les accès

# Configuration du client MQTT
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    mqtt_client.subscribe("uca/iot/piscine")

def on_message(client, userdata, msg):
    pool_data = msg.payload.decode()
    pool_info = json.loads(pool_data)
    
    pool_id = pool_info["info"]["ident"]

    # Mettre à jour l'état de la piscine dans MongoDB
    pools_collection.update_one(
        {"pool_id": pool_id},
        {"$set": {
            "info": pool_info.get("info", {}),
            "location": pool_info.get("location", {}),
            "net": pool_info.get("net", {}),
            "piscine": pool_info.get("piscine", {}),
            "regul": pool_info.get("regul", {}),
            "reporthost": pool_info.get("reporthost", {}),
            "status": pool_info.get("status", {}),
        }},
        upsert=True
    )

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    mqtt_client.connect("test.mosquitto.org", 1883)
    mqtt_client.loop_forever()

# Démarrer le client MQTT dans un thread séparé
mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.start()

# Route pour vérifier l'accès à la piscine
@app.route('/open', methods=['GET'])
def check_access():
    client_id = request.args.get('idu')
    pool_id = request.args.get('idswp')

    if not client_id or not pool_id:
        return render_template('index.html', message="Error: Missing parameters"), 400

    # Vérifier si l'utilisateur est déclaré
    user = users_collection.find_one({"clientID": client_id})
    if not user:
        return render_template('index.html', message="Access denied: User not found"), 404

    # Vérifier si la piscine existe et n'est pas déjà occupée
    pool = pools_collection.find_one({"pool_id": pool_id})
    if not pool:
        return render_template('index.html', message="Access denied: Pool not found"), 404

    if pool.get("piscine", {}).get("occuped", False):
        return render_template('index.html', message="Access denied: Pool already occupied"), 403

    # Convertir l'objet pool en JSON serializable
    pool_json = json.loads(json_util.dumps(pool))

    # Extraire les informations spécifiques
    temperature = pool_json["status"]["temperature"]
    occuped = pool_json["piscine"]["occuped"]
    hotspot = pool_json["piscine"]["hotspot"]
    location = pool_json["location"]

    # Enregistrer l'accès dans la collection access_logs
    access_logs_collection.insert_one({
        "client_id": client_id,
        "pool_id": pool_id,
        "temperature": temperature,
        "occuped": occuped,
        "hotspot": hotspot,
        "location": location,
        "timestamp": datetime.now()
    })

    # Si toutes les conditions sont remplies, accès accordé
    return render_template('index.html', message="Access granted", temperature=temperature, occuped=occuped, hotspot=hotspot), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
