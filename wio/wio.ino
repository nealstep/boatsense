#include <rpcWiFi.h>
#include <PubSubClient.h>
#include <TFT_eSPI.h>

#define BAUD 115200
#define DELAY_WIFI 500
#define DELAY_MQTT 5000
#define DELAY_LOOP 50
#define DELAY_CHECK 100

const char* SSID="Canobi_Build";
const char* PWD="swadekrap";
const char* BROKER="o2lte-2.home.bakerst.org";
const int BROKER_PORT=1883;
const char* TOPIC="sensors/#";
const char* ID="wio-1";

// wifi
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// display
TFT_eSPI tft = TFT_eSPI();

// counter
int loops;

void setup_tft(void) {
  tft.begin();
  tft.setRotation(3);
  tft.setTextFont(2);
  tft.fillScreen(TFT_WHITE);
}

void setup_wifi(void) {
  Serial.println("Wifi");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  Serial.println("Connecting");
  WiFi.begin(SSID, PWD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(DELAY_WIFI);
    Serial.println("Retrying WiFi");
    WiFi.begin(SSID, PWD);
  }
  Serial.println("Wifi Connected");
  Serial.print("IP: ");
  Serial.println (WiFi.localIP());
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.println(topic);
  tft.println(topic);
}

void mqtt_connect(void) {
  while (!mqttClient.connected()) {
    Serial.println("Connecting");
    if (mqttClient.connect(ID)) {
      Serial.println("connected");
      mqttClient.subscribe(TOPIC);
      Serial.println("Setup");
    }
    else {
      Serial.print("Failed, rc=");
      Serial.println(mqttClient.state());
      delay(DELAY_MQTT);
    }
  }
}

void setup_mqtt(void) {
  Serial.println("MQTT");
  mqttClient.setServer(BROKER, BROKER_PORT);
  mqttClient.setCallback(mqtt_callback);
  mqtt_connect();
}

void setup() {
  // initialize  serial ports:
  Serial.begin(BAUD);
  Serial.flush();
  Serial.println("Starting");
  setup_tft();
  setup_wifi();
  setup_mqtt();
  loops = 0;
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0, 2);
  tft.setTextColor(TFT_WHITE,TFT_BLACK);  
  tft.setTextSize(1);
  Serial.println("Started");
}

// handle buttons for screens
// display data (start with one screen)
void loop() {
  if (loops > DELAY_CHECK) {
    loops = 0;
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Reconnecting Wifi");
      setup_wifi();
      mqtt_connect();
    }
    Serial.println("Looped");
  }
  mqttClient.loop();
  delay(DELAY_LOOP);
  loops++;
}
