import os
import threading

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# Configuration de la connexion MongoDB
mongo_uri = "your_mongo_atlas_connection_string"
client = MongoClient(mongo_uri)
db = client['WaterBnB']
users_collection = db['users']
pools_collection = db['pools']

# Configuration du client MQTT
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    mqtt_client.subscribe("uca/iot/piscine")

def on_message(client, userdata, msg):
    pool_data = msg.payload.decode()
    # Supposons que pool_data est un JSON string
    import json
    pool_info = json.loads(pool_data)
    
    pool_id = pool_info.get("pool_id")
    occupied = pool_info.get("occupied", False)

    # Mettre à jour l'état de la piscine dans MongoDB
    pools_collection.update_one(
        {"pool_id": pool_id},
        {"$set": {"occupied": occupied}},
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
        return jsonify({"error": "Missing parameters"}), 400

    # Vérifier si l'utilisateur est déclaré
    user = users_collection.find_one({"client_id": client_id})
    if not user:
        return jsonify({"access": "denied", "reason": "User not found"}), 404

    # Vérifier si la piscine existe et n'est pas déjà occupée
    pool = pools_collection.find_one({"pool_id": pool_id})
    if not pool:
        return jsonify({"access": "denied", "reason": "Pool not found"}), 404

    if pool.get("occupied", False):
        return jsonify({"access": "denied", "reason": "Pool already occupied"}), 403

    # Si toutes les conditions sont remplies, accès accordé
    return jsonify({"access": "granted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))