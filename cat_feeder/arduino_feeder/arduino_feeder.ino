#include <SPI.h>
#include <Servo.h>
#include <MFRC522.h>

#define RST_PIN 9
#define SS_PIN 10

Servo s;
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  s.attach(7);
  s.write(0); // pocetna (zatvorena) pozicija poklopca
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("READY");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  String tagId = readTagId();

  Serial.print("TAG:");
  Serial.println(tagId);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  waitForResponse(2000); // ceka odgovor od Raspberry Pi-ja max 2 sekunde

  delay(1000); // debounce - sprecava da se ista kartica procita vise puta zaredom
}

String readTagId() {
  String tagId = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    byte b = rfid.uid.uidByte[i];
    if (b < 0x10) tagId += "0"; // vodeca nula da bi svaki bajt uvek imao 2 cifre
    tagId += String(b, HEX);
  }
  tagId.toUpperCase();
  return tagId;
}

void waitForResponse(unsigned long timeoutMs) {
  unsigned long startTime = millis();
  while (millis() - startTime < timeoutMs) {
    if (Serial.available() > 0) {
      String response = Serial.readStringUntil('\n');
      response.trim();
      if (response == "OPEN") {
        openFeeder(1000);
      }
      return;
    }
  }
}

void openFeeder(int d) {
  s.write(90);
  delay(d);
  s.write(0);
}
