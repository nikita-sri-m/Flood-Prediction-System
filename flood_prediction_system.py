from flask import Flask, request, jsonify, send_from_directory
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("flood_risk_dataset_india.csv")
data = data[['Latitude', 'Longitude', 'Rainfall (mm)', 'Water Level (m)', 'Humidity (%)']]
data.columns = ['Latitude', 'Longitude', 'Rainfall', 'RiverLevel', 'Humidity']
data['SoilMoisture'] = (0.7 * data['Rainfall']) + (0.3 * data['Humidity'])

def calculate_risk(rainfall, river, soil):
    return (0.5 * rainfall) + (0.3 * river) + (0.2 * soil)

def classify_risk(score):
    if score < 40: return "LOW"
    elif score < 70: return "MODERATE"
    else: return "HIGH"

@app.route("/predict", methods=["GET"])
def predict():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    row = data.iloc[(data['Latitude'] - lat).abs().argsort()[:1]].iloc[0]
    score = calculate_risk(row['Rainfall'], row['RiverLevel'], row['SoilMoisture'])
    level = classify_risk(score)
    return jsonify({
        "score": round(score, 2),
        "level": level,
        "rainfall": round(row['Rainfall'], 2),
        "river_level": round(row['RiverLevel'], 2),
        "humidity": round(row['Humidity'], 2),  # ← real values from dataset
        "soil_moisture": round(row['SoilMoisture'], 2),
        "matched_lat": round(row['Latitude'], 4),
        "matched_lon": round(row['Longitude'], 4)
    })

@app.route("/")
def index():
    return send_from_directory(".", "flood_prediction_system.html")

if __name__ == "__main__":
    app.run(debug=True)
