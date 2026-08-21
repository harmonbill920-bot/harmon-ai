from football_api import get_today_fixtures

from predictor_engine import predict_match


# ============================================================
# HARMON AI
# REAL MATCH PREDICTION TEST
# ============================================================

print()
print("================================================")
print("        HARMON AI - REAL MATCH TEST")
print("================================================")


# ============================================================
# GET TODAY'S MATCHES
# ============================================================

result = get_today_fixtures()


if not result["success"]:

    print()
    print("API ERROR:")
    print(result["error"])

    exit()


matches = result["data"].get(
    "response",
    []
)


print()
print(
    "Today's matches:",
    len(matches)
)


if not matches:

    print()
    print("Hakuna matches leo.")

    exit()


# ============================================================
# FIND MATCH
# ============================================================

selected_match = None


for match in matches:

    teams = match.get(
        "teams",
        {}
    )

    home = teams.get(
        "home",
        {}
    )

    away = teams.get(
        "away",
        {}
    )

    home_id = home.get(
        "id"
    )

    away_id = away.get(
        "id"
    )

    if home_id and away_id:

        selected_match = match

        break


if not selected_match:

    print()
    print(
        "Hakuna match yenye Team IDs."
    )

    exit()


# ============================================================
# MATCH INFORMATION
# ============================================================

fixture = selected_match.get(
    "fixture",
    {}
)

league = selected_match.get(
    "league",
    {}
)

teams = selected_match.get(
    "teams",
    {}
)

home = teams.get(
    "home",
    {}
)

away = teams.get(
    "away",
    {}
)


home_id = home.get(
    "id"
)

away_id = away.get(
    "id"
)

home_name = home.get(
    "name",
    "Home Team"
)

away_name = away.get(
    "name",
    "Away Team"
)

fixture_id = fixture.get(
    "id"
)


# ============================================================
# DISPLAY MATCH
# ============================================================

print()
print("================================================")
print("MATCH SELECTED")
print("================================================")

print()
print(
    "League:",
    league.get(
        "name",
        "Unknown"
    )
)

print(
    "Country:",
    league.get(
        "country",
        "Unknown"
    )
)

print(
    "Fixture ID:",
    fixture_id
)

print()

print(
    home_name,
    " VS ",
    away_name
)

print()

print(
    "Home ID:",
    home_id
)

print(
    "Away ID:",
    away_id
)


# ============================================================
# RUN HARMON AI
# ============================================================

print()
print("================================================")
print("RUNNING HARMON AI ANALYSIS")
print("================================================")

print()
print(
    "Collecting recent form..."
)

print(
    "Collecting goals data..."
)

print(
    "Collecting H2H..."
)

print(
    "Calculating team strength..."
)

print(
    "Calculating probabilities..."
)

print()


prediction = predict_match(

    home_id,

    away_id,

    use_api_prediction=False

)


# ============================================================
# CHECK RESULT
# ============================================================

if not prediction["success"]:

    print()
    print("================================================")
    print("PREDICTION ERROR")
    print("================================================")

    print()
    print(
        prediction["error"]
    )

    exit()


# ============================================================
# DISPLAY 1X2
# ============================================================

print()
print("================================================")
print("           1X2 PROBABILITY")
print("================================================")

print()

print(
    home_name,
    "WIN:",
    prediction[
        "home_probability"
    ],
    "%"
)

print(
    "DRAW:",
    prediction[
        "draw_probability"
    ],
    "%"
)

print(
    away_name,
    "WIN:",
    prediction[
        "away_probability"
    ],
    "%"
)


# ============================================================
# EXPECTED GOALS
# ============================================================

print()
print("================================================")
print("           EXPECTED GOALS")
print("================================================")

print()

print(
    home_name,
    ":",
    prediction[
        "home_xg"
    ]
)

print(
    away_name,
    ":",
    prediction[
        "away_xg"
    ]
)


# ============================================================
# OVER / UNDER
# ============================================================

print()
print("================================================")
print("           OVER / UNDER")
print("================================================")

ou = prediction[
    "over_under"
]

print()

print(
    "Over 0.5:",
    ou["over_0_5"],
    "%"
)

print(
    "Over 1.5:",
    ou["over_1_5"],
    "%"
)

print(
    "Over 2.5:",
    ou["over_2_5"],
    "%"
)

print(
    "Over 3.5:",
    ou["over_3_5"],
    "%"
)

print()

print(
    "Under 0.5:",
    ou["under_0_5"],
    "%"
)

print(
    "Under 1.5:",
    ou["under_1_5"],
    "%"
)

print(
    "Under 2.5:",
    ou["under_2_5"],
    "%"
)

print(
    "Under 3.5:",
    ou["under_3_5"],
    "%"
)


# ============================================================
# BTTS
# ============================================================

print()
print("================================================")
print("               BTTS")
print("================================================")

btts = prediction[
    "btts"
]

print()

print(
    "BTTS YES:",
    btts["yes"],
    "%"
)

print(
    "BTTS NO:",
    btts["no"],
    "%"
)


# ============================================================
# DOUBLE CHANCE
# ============================================================

print()
print("================================================")
print("           DOUBLE CHANCE")
print("================================================")

dc = prediction[
    "double_chance"
]

print()

print(
    "1X:",
    dc["1X"],
    "%"
)

print(
    "X2:",
    dc["X2"],
    "%"
)

print(
    "12:",
    dc["12"],
    "%"
)


# ============================================================
# STRONGEST MARKET
# ============================================================

strongest = prediction[
    "strongest_market"
]

print()
print("================================================")
print("       HARMON AI STRONGEST MARKET")
print("================================================")

print()

print(
    "Market:",
    strongest["market"]
)

print(
    "Probability:",
    strongest["probability"],
    "%"
)


# ============================================================
# CONFIDENCE
# ============================================================

print()
print("================================================")
print("              AI CONFIDENCE")
print("================================================")

print()

print(
    prediction["confidence"],
    "%"
)


# ============================================================
# TEAM STRENGTH
# ============================================================

print()
print("================================================")
print("            TEAM STRENGTH")
print("================================================")

print()

print(
    home_name,
    ":",
    prediction["home_strength"],
    "%"
)

print(
    away_name,
    ":",
    prediction["away_strength"],
    "%"
)


# ============================================================
# FORM
# ============================================================

print()
print("================================================")
print("              RECENT FORM")
print("================================================")

home_form = prediction[
    "home_form"
]

away_form = prediction[
    "away_form"
]

print()

print(
    home_name,
    ":",
    " ".join(
        home_form["form"]
    )
)

print(
    away_name,
    ":",
    " ".join(
        away_form["form"]
    )
)


# ============================================================
# H2H
# ============================================================

print()
print("================================================")
print("                 H2H")
print("================================================")

h2h = prediction[
    "h2h"
]

print()

print(
    "Previous matches:",
    h2h["matches"]
)

print(
    "Home wins:",
    h2h["home_wins"]
)

print(
    "Draws:",
    h2h["draws"]
)

print(
    "Away wins:",
    h2h["away_wins"]
)


# ============================================================
# FINAL
# ============================================================

print()
print("================================================")
print("        HARMON AI ANALYSIS COMPLETE")
print("================================================")

print()

print(
    "Statistical analysis only."
)

print(
    "No prediction can guarantee"
)

print(
    "a match result."
)

print()