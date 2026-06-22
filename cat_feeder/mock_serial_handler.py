import time
import threading
import random
import database as db


class MockSerialHandler:
    def __init__(self):
        self.running = False
        self.last_event = {"tag_id": None, "status": None, "time": None}

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

    def _handle_tag(self, tag_id):
        if db.tag_exists(tag_id):
            db.update_scan(tag_id)
            self.write(b"OPEN\n")
            self.last_event = {
                "tag_id": tag_id,
                "status": "opened",
                "time": time.time()
            }
            print(f"[MOCK] Known tag {tag_id} -> OPEN")
        else:
            db.register_tag(tag_id)
            self.last_event = {
                "tag_id": tag_id,
                "status": "registered",
                "time": time.time()
            }
            print(f"[MOCK] New tag {tag_id} -> registered")

    def _loop(self):
        fake_tags = ["ABC123", "DOG456", "CAT789"]

        while self.running:
            time.sleep(random.randint(5, 10))

            tag_id = random.choice(fake_tags)

            self._handle_tag(tag_id)

    def write(self, data):
        print(f"[MOCK WRITE] {data}")