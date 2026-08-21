import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

print("Loading football data...")

# Load dataset
df = pd.read_csv("data/matches.csv")

# Create team encoder
team_encoder = LabelEncoder()

all_teams = pd.concat([
    df["home_team"],
    df["away_team"]
]).unique()

team_encoder.fit(all_teams)

# Encode teams
df["home_team_encoded"] = team_encoder.transform(
    df["home_team"]
)

df["away_team_encoded"] = team_encoder.transform(
    df["away_team"]
)

# Features
X = df[
    [
        "home_team_encoded",
        "away_team_encoded",
        "home_form",
        "away_form"
    ]
]

# Target
y = df["result"]

print("Training AI model...")

# Create model
model = RandomForestClassifier(
    n_estimators=300,
    random_state=42
)

# Train model
model.fit(X, y)

# Save model
joblib.dump(
    model,
    "model/predictor.pkl"
)

joblib.dump(
    team_encoder,
    "model/team_encoder.pkl"
)

print()
print("==============================")
print("HARMON AI PREDICTOR")
print("==============================")
print("Model trained successfully!")
print("Model saved in /model/")
print("==============================")