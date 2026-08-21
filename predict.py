import pandas as pd
import joblib

MODEL_PATH = "model/predictor.pkl"
ENCODER_PATH = "model/team_encoder.pkl"

model = joblib.load(MODEL_PATH)
team_encoder = joblib.load(ENCODER_PATH)


def predict_match(home_team, away_team, home_form, away_form):

    if home_team not in team_encoder.classes_:
        return {"error": f"{home_team} not found"}

    if away_team not in team_encoder.classes_:
        return {"error": f"{away_team} not found"}

    home_encoded = team_encoder.transform([home_team])[0]
    away_encoded = team_encoder.transform([away_team])[0]

    data = pd.DataFrame([
        {
            "home_team_encoded": home_encoded,
            "away_team_encoded": away_encoded,
            "home_form": home_form,
            "away_form": away_form
        }
    ])

    prediction = model.predict(data)[0]
    probabilities = model.predict_proba(data)[0]

    probability_data = {}

    for cls, probability in zip(model.classes_, probabilities):
        probability_data[cls] = round(probability * 100, 2)

    result_names = {
        "H": "Home Win",
        "D": "Draw",
        "A": "Away Win"
    }

    return {
        "prediction": result_names[prediction],
        "home_probability": probability_data.get("H", 0),
        "draw_probability": probability_data.get("D", 0),
        "away_probability": probability_data.get("A", 0)
    }