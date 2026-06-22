# Hranilica za mačke — RFID + Servo + Raspberry Pi + Flask

## Struktura projekta
```
cat_feeder/
├── app.py                 # Flask server
├── database.py             # SQLite baza (rfid_tags)
├── serial_handler.py        # komunikacija sa Arduinom
├── requirements.txt
├── templates/
│   └── index.html
└── arduino_feeder/
    └── arduino_feeder.ino  # ažuriran Arduino kod
```

## Kako radi
1. Arduino čita RFID tag i šalje preko USB Serial-a: `TAG:<id>`.
2. Python `serial_handler.py` u pozadinskom thread-u čita tu liniju:
   - ako tag **ne postoji** u bazi → upisuje ga (registracija), feeder se NE otvara.
   - ako tag **već postoji** u bazi → šalje nazad `OPEN\n` Arduinu, koji pokreće servo (`open(1000)`).
3. Flask servira veb stranicu (`/`) sa listom registrovanih tagova i poslednjim događajem, plus JSON API (`/api/tags`).

## 1. Prebacivanje fajlova na Raspberry Pi
U Bitvise SSH klijentu otvori **SFTP** tab (ne samo terminal) i prevuci ceo `cat_feeder` folder na Pi, npr. u `/home/pi/cat_feeder`.

## 2. Podešavanje virtuelnog okruženja (u Bitvise terminalu)
```bash
sudo apt update
sudo apt install python3-venv python3-pip -y

cd /home/pi/cat_feeder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Dozvola za pristup serial portu
Korisnik mora biti u `dialout` grupi da bi mogao da čita/piše na serial port:
```bash
sudo usermod -a -G dialout $USER
```
Posle ovoga je potrebno da se ponovo uloguješ (zatvori i otvori Bitvise konekciju) da bi promena dejstvovala.

## 4. Provera tačnog serial porta
Priključi Arduino preko USB-a, pa proveri:
```bash
ls /dev/tty*
```
Najčešće je `/dev/ttyACM0` (Arduino Uno) ili `/dev/ttyUSB0`. Ako se razlikuje, izmeni `SERIAL_PORT` u `serial_handler.py`.

> **Bitno:** ako koristiš Arduino IDE da upload-uješ skicu na Arduino dok je on povezan na Pi, prvo zatvori Flask server (serial port ne može da bude otvoren na dva mesta istovremeno).

## 5. Pokretanje servera
```bash
source venv/bin/activate   # ako već nije aktiviran
$env:MOCK_MODE="true"; py .\cat_feeder\app.py #za testiranje
$env:MOCK_MODE="false"; py .\cat_feeder\app.py #realno okruženje
```
Web interfejs: `http://<IP_RASPBERRY_PI>:5000`
