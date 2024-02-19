
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi
const char *ssid = "iPhoneEarl";      // Change this to your WiFi SSID
const char *password = "1234567890";  // Change this to your WiFi password

// MQTT Broker
const char *mqtt_broker = "69.109.130.206";
const char *topic = "weather/test";
const char *mqtt_username = "power";
const char *mqtt_password = "nD3M$3AhDob2K+xhAE";
const int mqtt_port = 1883;


WiFiClient espClient;
PubSubClient client(espClient);

#define WindDir_PIN A0   // the number of the Wind Direction sensor pin
#define pinInterrupt 9  // the number of the Wind Speed sensor pin

int speed_value = 0;
float wind_dir = 0;

int Count = 0;
int sensortime = 0;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 1000;

void IRAM_ATTR onChange() {
  Serial.println("change..");
  if (digitalRead(pinInterrupt) == LOW)
    Count++;
}

int wind_direction() {
  int adc_value = analogRead(WindDir_PIN);
  Serial.print("adc val=");
  Serial.println(adc_value);

  wind_dir = (adc_value + 70) / 140;
  Serial.println(wind_dir);
  return wind_dir;
}

void wind_speed() {
  if ((millis() - lastDebounceTime) > debounceDelay) {
    lastDebounceTime = millis();
    speed_value = Count * 8.75 * 0.01;
    Serial.print("Wind Speed: ");
    Serial.print(speed_value);  // in m/s
    Serial.println("m/s");
    Count = 0;
  }
}

void setup() {
  // Set software serial baud to 115200;
  Serial.begin(115200);
  // Connecting to a WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }

  Serial.println("Connected to the Wi-Fi network");
  //connecting to a mqtt broker
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);

  while (!client.connected()) {
    String client_id = "esp32-wind-";
    client_id += String(WiFi.macAddress());
    Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Public EMQX MQTT broker connected");
    } else {
      Serial.print("failed with state ");
      Serial.println(client.state());
      delay(2000);
    }
  }
  // Publish and subscribe
  client.publish(topic, "ESP32 Wind Checking in");
  client.subscribe(topic);

  pinMode(pinInterrupt, INPUT_PULLUP);
  attachInterrupt(pinInterrupt, onChange, FALLING);
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  Serial.println("-----------------------");
}

void loop() {
  client.loop();
  delay(2000);
  wind_speed();
  Serial.print("Wind Speed:");
  Serial.println(speed_value);
}