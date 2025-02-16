#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>

// Switch sensor pin (using the built-in ADC - A0 on ESP8266)
const int SWITCH_PIN = A0;
const int LED_PIN = LED_BUILTIN;

// State change detection
int lastSwitchState = LOW;
int currentSwitchState = LOW;

// Mute detection timing
const unsigned long MUTE_WINDOW = 5000; // 5 seconds window for mute toggle
unsigned long offTime = 0;
bool muteAction = false; // To track if mute/unmute is triggered

// Wi-Fi credentials (Replace these with your network details)
const char* ssid = "home network";
const char* password = "anish2012";

// State variables
bool handRaised = false;
bool isMuted = false;
bool wifiMode = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  
  Serial.println("\n--- Switch Control Starting ---");
  
  // Try to connect to Wi-Fi
//  WiFi.begin(ssid, password);
  
//  int attempts = 0;
//  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
//    delay(500);
//    Serial.print(".");
//    attempts++;
//  }
  
  {
    wifiMode = false;
    Serial.println("Running in Serial-only mode");
  }

  // Startup indication
  for (int i = 0; i < (wifiMode ? 3 : 1); i++) {
    digitalWrite(LED_PIN, LOW);
    delay(100);
    digitalWrite(LED_PIN, HIGH);
    delay(100);
  }

  Serial.println("Ready! Controls:");
  Serial.println("- OFF → ON: Toggle hand raise");
  Serial.println("- ON → OFF → ON within 5 seconds: Toggle mute");
}

void loop() {
  // Read the state of the switch
  int analogValue = analogRead(SWITCH_PIN);
  currentSwitchState = (analogValue > 500) ? HIGH : LOW;

  // ON → OFF: Start timer to check for return to ON
  if (lastSwitchState == HIGH && currentSwitchState == LOW) {
    offTime = millis(); // Record the time when it turned OFF
    muteAction = false; // Reset mute action
  }

  // OFF → ON within 5 seconds: Toggle mute
  if (lastSwitchState == LOW && currentSwitchState == HIGH) {
    if (millis() - offTime < MUTE_WINDOW && millis() - offTime > 1111) {
      isMuted = !isMuted;
      Serial.println(isMuted ? "MUTE" : "UNMUTE");
      blinkLED(3);  // Triple blink for mute/unmute
      muteAction = true; // Mark mute action to avoid hand raise
    }
  }

  // OFF → ON: Toggle hand raise (only if not a mute action)
  if (lastSwitchState == LOW && currentSwitchState == HIGH && !muteAction) {
    handRaised = !handRaised;
    Serial.println(handRaised ? "HAND_RAISE" : "HAND_LOWER");
    blinkLED(1);
  }

  lastSwitchState = currentSwitchState;
  delay(10);
}

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(LED_PIN, HIGH);
    delay(50);
  }
}
