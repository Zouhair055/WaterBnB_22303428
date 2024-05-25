#include <WiFi.h>
#include <PubSubClient.h>
#include "wifi_utils.h"
#include "DHT.h"
#include "ArduinoJson.h"

bool isPOccupied = true;
const int ledPin = 19; // LED Pin

#define DHTPIN 23  // Pin du capteur DHT11
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const char* mqtt_server = "test.mosquitto.org";

#define TOPIC "uca/iot/piscine"
#define HOTSPOT_TOPIC "uca/iot/piscine/hotspot"

WiFiClient espClient;
PubSubClient mqttclient(espClient);

String hostname = "Mon petit objet ESP32";

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  dht.begin();

  wifi_connect_multi(hostname);   
  
  // Afficher l'état de la connexion WiFi
  Serial.print("WiFi status: ");
  Serial.println(WiFi.status());

  mqttclient.setServer(mqtt_server, 1883);
  mqttclient.setBufferSize(1024);
  mqttclient.setCallback(mqtt_pubcallback); 

  mqtt_subscribe_mytopics(); // Abonnement initial
}


void set_LED(int v) {
    digitalWrite(ledPin, v);
}

float get_Temperature() {
  return dht.readTemperature();
}

void mqtt_pubcallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }
  Serial.println(messageTemp);
  
  if (String(topic) == HOTSPOT_TOPIC) {
    if (messageTemp.equalsIgnoreCase("true")) {
      set_LED(HIGH);
    } else {
      set_LED(LOW);
    }
  }
}

void mqtt_subscribe_mytopics() {
  while (!mqttclient.connected()) {
    Serial.print("Attempting MQTT connection...");
    String mqttclientId = "P_22000286";
    if (mqttclient.connect(mqttclientId.c_str())) {
      Serial.println("connected");
      mqttclient.subscribe(TOPIC, 1);
      mqttclient.subscribe(HOTSPOT_TOPIC, 1);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttclient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

const int lightThreshold = 500;
int lightValue = 0;

void loop() {
  mqttclient.loop(); // Gestion des messages MQTT

  unsigned long currentTime = millis();
  static unsigned long lastPublishTime = 0;
  const long period = 5000; 

  if (mqttclient.connected() && currentTime - lastPublishTime > period) {
    lastPublishTime = currentTime;

    float temperature = get_Temperature();

    // Utilisation de la bibliothèque ArduinoJson pour créer le payload
    String jsonPayload = sendJsonPayload(temperature); // Utilisez la température lue

    const char* payload = jsonPayload.c_str();

    Serial.print("Publish payload: ");
    Serial.println(payload);
    Serial.print("on topic: ");
    Serial.println(TOPIC);

    mqttclient.publish(TOPIC, payload);
  }
}

String sendJsonPayload(float temperature) {
  StaticJsonDocument<1000> jdoc;

  int lightIntensity = 4095 - analogRead(A5); // Lire la valeur du capteur de lumière
  if (lightIntensity > 500) {
  isPOccupied = true;
  }
  else{
      isPOccupied = false;
    }

  jdoc["status"]["temperature"] = temperature;
  jdoc["status"]["light"] = lightIntensity;
  jdoc["location"]["gps"]["lat"] = "43.62344";
  jdoc["location"]["gps"]["lon"] = "7.05231";
  jdoc["info"]["ident"] = "P_22303428";
  jdoc["info"]["user"] = "DKHISSI - EL ALAMI";
  jdoc["info"]["loc"] = "Paris";
  jdoc["piscine"]["hotspot"] = false;

  // Si la lumière détectée est supérieure au seuil, la piscine est considérée comme occupée
  jdoc["piscine"]["occuped"] = isPOccupied;

  String payload;
  serializeJson(jdoc, payload);

  return payload;
}
