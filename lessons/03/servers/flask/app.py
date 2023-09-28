from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/median", methods=['POST'])
def find_median():
    data = request.get_json(force=True)
    numbers = [404]
    if isinstance(data, dict):
        numbers = sorted(data.get("numbers", []))
    return jsonify({"median": numbers[len(numbers)//2]})
