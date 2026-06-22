from flask import Flask, jsonify, render_template, request
from flasgger import Swagger
import database as db
import os

print("DB FILE USED:", db.__file__)
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

if MOCK_MODE:
    from mock_serial_handler import MockSerialHandler
    serial_handler = MockSerialHandler()
else:
    from serial_handler import SerialHandler
    serial_handler = SerialHandler()


app = Flask(__name__)
Swagger(app)


@app.route("/")
def index():
    tags = db.get_all_tags()
    return render_template("index.html", tags=tags, last_event=serial_handler.last_event)


@app.route("/api/tags")
def api_tags():
    """
    Prikaz svih registrovanih RFID tagova
    ---
    responses:
      200:
        description: Lista svih registrovanih tagova
        examples:
          application/json:
            - id: 1
              tag_id: "ABC123"
              name: "Maca"
              registered_at: "2025-01-01 10:00:00"
              last_scan: "2025-01-02 08:30:00"
              scan_count: 5
    """
    return jsonify(db.get_all_tags())


@app.route("/api/last_event")
def api_last_event():
    """
    Prikaz poslednjeg RFID događaja (skeniranja)
    ---
    responses:
      200:
        description: Poslednji događaj
        examples:
          application/json:
            tag_id: "ABC123"
            status: "opened"
            time: 1704067200.0
    """
    return jsonify(serial_handler.last_event)


@app.route("/api/tags/<tag_id>", methods=["DELETE"])
def api_delete_tag(tag_id):
    """
    Brisanje registrovanog RFID taga
    ---
    parameters:
      - name: tag_id
        in: path
        type: string
        required: true
        description: Identifikator taga koji se briše
    responses:
      200:
        description: Tag uspešno obrisan
        examples:
          application/json:
            status: "deleted"
    """
    db.delete_tag(tag_id)
    return jsonify({"status": "deleted"})


@app.route("/api/tags/<tag_id>/name", methods=["POST"])
def api_set_name(tag_id):
    """
    Postavljanje ili izmena imena za registrovani tag
    ---
    parameters:
      - name: tag_id
        in: path
        type: string
        required: true
        description: Identifikator taga
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Maca"
    responses:
      200:
        description: Ime uspešno ažurirano
        examples:
          application/json:
            status: "updated"
    """
    name = request.json.get("name") if request.is_json else None
    db.set_name(tag_id, name)
    return jsonify({"status": "updated"})


@app.route("/api/tags/<tag_id>/feeding-times", methods=["POST"])
def api_add_feeding_time(tag_id):
    """
    Dodavanje vremena hranjenja za određeni tag
    ---
    parameters:
      - name: tag_id
        in: path
        type: string
        required: true
        description: Identifikator taga
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            time:
              type: string
              example: "08:00"
    responses:
      200:
        description: Vreme hranjenja uspešno dodato
        examples:
          application/json:
            status: "added"
            time: "08:00"
      400:
        description: Vreme nije prosleđeno
        examples:
          application/json:
            error: "time required"
    """
    data = request.get_json()
    time_str = data.get("time")

    if not time_str:
        return jsonify({"error": "time required"}), 400

    db.add_feeding_time(tag_id, time_str)
    return jsonify({"status": "added", "time": time_str})


@app.route("/api/tags/<tag_id>/feeding-times", methods=["GET"])
def api_get_feeding_times(tag_id):
    """
    Prikaz rasporeda hranjenja za određeni tag
    ---
    parameters:
      - name: tag_id
        in: path
        type: string
        required: true
        description: Identifikator taga
    responses:
      200:
        description: Lista rasporeda hranjenja, sortirana po vremenu
        examples:
          application/json:
            - id: 1
              tag_id: "ABC123"
              time: "08:00"
              created_at: "2025-01-01 10:00:00"
    """
    return jsonify(db.get_feeding_times(tag_id))


@app.route("/api/feeding-times/<int:time_id>", methods=["DELETE"])
def api_delete_feeding_time(time_id):
    """
    Brisanje određenog vremena hranjenja
    ---
    parameters:
      - name: time_id
        in: path
        type: integer
        required: true
        description: ID unosa rasporeda hranjenja koji se briše
    responses:
      200:
        description: Vreme hranjenja uspešno obrisano
        examples:
          application/json:
            status: "deleted"
    """
    db.delete_feeding_time(time_id)
    return jsonify({"status": "deleted"})


@app.route("/api/health", methods=["GET"])
def api_health():
    """
    Provera statusa aplikacije
    ---
    responses:
      200:
        description: Aplikacija je aktivna
        examples:
          application/json:
            status: "ok"
            mock_mode: true
            serial_running: true
    """
    return jsonify({
        "status": "ok",
        "mock_mode": MOCK_MODE,
        "serial_running": serial_handler.running
    })


if __name__ == "__main__":
    db.init_db()
    serial_handler.start()

    print(f"MOCK MODE = {MOCK_MODE}")

    app.run(host="0.0.0.0", port=5000, debug=False)