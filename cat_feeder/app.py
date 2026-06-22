from flask import Flask, jsonify, render_template, request
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


@app.route("/")
def index():
    tags = db.get_all_tags()
    return render_template("index.html", tags=tags, last_event=serial_handler.last_event)


@app.route("/api/tags")
def api_tags():
    return jsonify(db.get_all_tags())


@app.route("/api/last_event")
def api_last_event():
    return jsonify(serial_handler.last_event)


@app.route("/api/tags/<tag_id>", methods=["DELETE"])
def api_delete_tag(tag_id):
    db.delete_tag(tag_id)
    return jsonify({"status": "deleted"})


@app.route("/api/tags/<tag_id>/name", methods=["POST"])
def api_set_name(tag_id):
    name = request.json.get("name") if request.is_json else None
    db.set_name(tag_id, name)
    return jsonify({"status": "updated"})


@app.route("/api/tags/<tag_id>/feeding-times", methods=["POST"])
def api_add_feeding_time(tag_id):
    data = request.get_json()
    time_str = data.get("time")

    if not time_str:
        return jsonify({"error": "time required"}), 400

    db.add_feeding_time(tag_id, time_str)

    return jsonify({"status": "added", "time": time_str})


@app.route("/api/tags/<tag_id>/feeding-times", methods=["GET"])
def api_get_feeding_times(tag_id):
    return jsonify(db.get_feeding_times(tag_id))


@app.route("/api/feeding-times/<int:time_id>", methods=["DELETE"])
def api_delete_feeding_time(time_id):
    db.delete_feeding_time(time_id)
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    db.init_db()
    serial_handler.start()

    print(f"MOCK MODE = {MOCK_MODE}")

    app.run(host="0.0.0.0", port=5000, debug=False)