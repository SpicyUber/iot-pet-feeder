#include <SPI.h>
#include <MFRC522.h>
#define RST_PIN 9
#define SS_PIN 10

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
Serial.begin(9600);
SPI.begin();
rfid.PCD_Init();
Serial.println("Prisloni karticu/tag...");
}

void loop() {
if (!rfid.PICC_IsNewCardPresent()) return;
if (!rfid.PICC_ReadCardSerial()) return;

Serial.print("Tag ID: ");
for (byte i = 0; i < rfid.uid.size; i++) {
Serial.print(rfid.uid.uidByte[i], HEX);
}
Serial.println();
rfid.PICC_HaltA();
while (Serial.available() > 0) {
  Serial.read(); 
}
}