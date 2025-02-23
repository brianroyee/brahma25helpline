from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
  return "Running"

@app.route('/data', methods=['GET'])
def _data():
  try:
    with open('data/bot_stats.json', 'r') as f:
      data = f.read()
    return jsonify(data)
  except Exception as e:
    return jsonify(
      {
        "Error": str(e)
      }
    )

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()
