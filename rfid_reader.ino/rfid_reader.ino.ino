#include <SPI.h>
#include <Servo.h>
#include <MFRC522.h>
#define RST_PIN 9
#define SS_PIN 10
Servo s;

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
s.attach(7);
Serial.begin(9600);
SPI.begin();
rfid.PCD_Init();
Serial.println("\nPrisloni karticu/tag...");
}

void loop() {
if (!rfid.PICC_IsNewCardPresent()) return;
if (!rfid.PICC_ReadCardSerial()) return;

//Serial.print("Tag ID: ");
String tagId = "";
for (byte i = 0; i < rfid.uid.size; i++) {
  byte b = rfid.uid.uidByte[i];
  if (b < 0x10) tagId += "0";   // dodaj vodecu nulu
  tagId += String(b, HEX);
  Serial.print(b < 0x10 ? "0" : "");
  Serial.print(b, HEX);
}
tagId.toUpperCase();             // izjednaci slova

Serial.print(" | tagId=");
Serial.println(tagId);           // OBAVEZNO odštampaj da vidiš stvarnu vrednost

rfid.PICC_HaltA();
while (Serial.available() > 0) Serial.read();

if (tagId == "AE0F8063") {        // ova vrednost je verovatno pogresna/nepotpuna
  Serial.println("MATCH");
  open(1000);
}

}

void open(int d)
{
  s.write(180);
  delay(d);
  s.write(0);
}