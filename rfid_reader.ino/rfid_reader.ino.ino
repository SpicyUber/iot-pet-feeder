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
Serial.print(b, HEX);
tagId += String(b, HEX);
}
Serial.print(';');
//Serial.println();
rfid.PICC_HaltA();
while (Serial.available() > 0) {
  Serial.read(); 
}
if(tagId == "5831989")
{
  open(1000);
}

}

void open(int d)
{
  s.write(90);
  delay(d);
  s.write(0);
}