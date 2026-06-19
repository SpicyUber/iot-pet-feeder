from flask import Flask, jsonify, render_template, request
import database as db
from serial_handler import serial_handler

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


if __name__ == "__main__":
    db.init_db()
    serial_handler.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
