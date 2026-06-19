import serial
import threading
import time
import database as db

# VAZNO: proveri tacan port komandom "ls /dev/tty*" pre i posle ukljucivanja
# Arduina preko USB-a. Obicno je /dev/ttyACM0 ili /dev/ttyUSB0.
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


class SerialHandler:
    def __init__(self, port=SERIAL_PORT, baud=BAUD_RATE):
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        self.last_event = {"tag_id": None, "status": None, "time": None}

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2)  # Arduino se resetuje kad se serial port otvori, treba sacekati

    def start(self):
        self.connect()
        self.running = True
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()
        print(f"Serial konekcija uspostavljena na {self.port}")

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _listen(self):
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line.startswith("TAG:"):
                    tag_id = line.replace("TAG:", "").strip()
                    self._handle_tag(tag_id)
            except Exception as e:
                print(f"Greska pri citanju serial porta: {e}")
                time.sleep(1)

    def _handle_tag(self, tag_id):
        if db.tag_exists(tag_id):
            db.update_scan(tag_id)
            self.ser.write(b"OPEN\n")
            self.last_event = {"tag_id": tag_id, "status": "opened", "time": time.time()}
            print(f"Poznata kartica {tag_id} -> saljem OPEN")
        else:
            db.register_tag(tag_id)
            self.last_event = {"tag_id": tag_id, "status": "registered", "time": time.time()}
            print(f"Nova kartica {tag_id} -> registrovana u bazu")


serial_handler = SerialHandler()
