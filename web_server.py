from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)

# Function to load the current state from a JSON file
def load_current_state():
    filename = 'logs/ipo_state.json'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {"stable_ipos": [], "unstable_ipos": []}

@app.route('/')
def index():
    state = load_current_state()
    return render_template('index.html', stable_ipos=state["stable_ipos"], unstable_ipos=state["unstable_ipos"])

@app.route('/api/ipos')
def get_ipos():
    state = load_current_state()
    return jsonify(state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)