#include <rpcWiFi.h>
#include <PubSubClient.h>
#include <TFT_eSPI.h>

#define BAUD 115200
#define DELAY_WIFI 500
#define DELAY_MQTT 5000
#define DELAY_LOOP 5
#define DELAY_CHECK 1000

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
uint16_t loops;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 500000;

// screen tracker
char screen = 'A';

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

void setup_buttons(void) {
  pinMode(WIO_KEY_A, INPUT_PULLUP);
  pinMode(WIO_KEY_B, INPUT_PULLUP);
  pinMode(WIO_KEY_C, INPUT_PULLUP);
}

void setup_vars(void) {
  
}

void set_screen(void) {
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0, 2);
  tft.setTextColor(TFT_WHITE,TFT_BLACK);  
  tft.setTextSize(2);  
}

void setup() {
  // initialize  serial ports:
  Serial.begin(BAUD);
  Serial.flush();
  Serial.println("Starting");

  // setup devices
  setup_tft();
  setup_wifi();
  setup_mqtt();
  setup_buttons();
  setup_vars();

  // init constants
  loops = 0;
  lastDebounceTime = 0;
  screen = 'A';

  // setup screen
  set_screen();

  // ready
  Serial.println("Started");
}

void check_buttons(void) {
  char button;
  long currentTime = micros();
  
  button = '_';
  if (digitalRead(WIO_KEY_A) == LOW) {
    button = 'A';
  } else if (digitalRead(WIO_KEY_B) == LOW) {
    button = 'B';
  } else if (digitalRead(WIO_KEY_C) == LOW) {
    button = 'C';
  }
  if (button != '_') {
    if ((currentTime - lastDebounceTime) > DEBOUNCE_DELAY) {
      lastDebounceTime = currentTime;
      Serial.print("Button ");
      Serial.println(button);
      if (screen != button) {
        screen = button;
        set_screen();
      }
    }
  }
}

// handle buttons for screens
// display data (start with one screen)
void loop() {
  check_buttons();
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
