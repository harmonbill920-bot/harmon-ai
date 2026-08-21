from football_api import (
    get_today_fixtures,
    get_team_recent_form,
    get_h2h_summary
)


# ============================================================
# HARMON AI
# FORM DATA TEST
# ============================================================

print()
print("==============================================")
print("       HARMON AI - FORM DATA TEST")
print("==============================================")


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
    print("Hakuna matches zilizopatikana leo.")

    exit()


# ============================================================
# FIND FIRST MATCH WITH TWO TEAMS
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

    if (
        home.get("id")
        and
        away.get("id")
    ):

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


# ============================================================
# DISPLAY MATCH
# ============================================================

print()
print("==============================================")
print("SELECTED MATCH")
print("==============================================")


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
    fixture.get(
        "id",
        "Unknown"
    )
)


print()
print(
    home_name,
    " VS ",
    away_name
)


print()
print(
    "Home Team ID:",
    home_id
)


print(
    "Away Team ID:",
    away_id
)


# ============================================================
# HOME TEAM FORM
# ============================================================

print()
print("==============================================")
print("HOME TEAM - LAST MATCHES")
print("==============================================")


print()
print(
    "Team:",
    home_name
)


print(
    "Loading recent matches..."
)


home_form = get_team_recent_form(
    home_id,
    10
)


if not home_form["success"]:

    print()
    print("HOME FORM ERROR:")
    print(home_form["error"])

else:

    print()

    print(
        "Matches:",
        home_form["matches"]
    )

    print(
        "Wins:",
        home_form["wins"]
    )

    print(
        "Draws:",
        home_form["draws"]
    )

    print(
        "Losses:",
        home_form["losses"]
    )

    print(
        "Goals For:",
        home_form["goals_for"]
    )

    print(
        "Goals Against:",
        home_form["goals_against"]
    )

    print(
        "Points:",
        home_form["points"]
    )

    print(
        "Points/Game:",
        home_form["points_per_game"]
    )

    print(
        "Goals/Game:",
        home_form["goals_per_game"]
    )

    print(
        "Conceded/Game:",
        home_form["conceded_per_game"]
    )

    print(
        "Form:",
        " ".join(
            home_form["form"]
        )
    )


# ============================================================
# AWAY TEAM FORM
# ============================================================

print()
print("==============================================")
print("AWAY TEAM - LAST MATCHES")
print("==============================================")


print()
print(
    "Team:",
    away_name
)


print(
    "Loading recent matches..."
)


away_form = get_team_recent_form(
    away_id,
    10
)


if not away_form["success"]:

    print()
    print("AWAY FORM ERROR:")
    print(away_form["error"])

else:

    print()

    print(
        "Matches:",
        away_form["matches"]
    )

    print(
        "Wins:",
        away_form["wins"]
    )

    print(
        "Draws:",
        away_form["draws"]
    )

    print(
        "Losses:",
        away_form["losses"]
    )

    print(
        "Goals For:",
        away_form["goals_for"]
    )

    print(
        "Goals Against:",
        away_form["goals_against"]
    )

    print(
        "Points:",
        away_form["points"]
    )

    print(
        "Points/Game:",
        away_form["points_per_game"]
    )

    print(
        "Goals/Game:",
        away_form["goals_per_game"]
    )

    print(
        "Conceded/Game:",
        away_form["conceded_per_game"]
    )

    print(
        "Form:",
        " ".join(
            away_form["form"]
        )
    )


# ============================================================
# HEAD TO HEAD
# ============================================================

print()
print("==============================================")
print("HEAD TO HEAD")
print("==============================================")


print()
print(
    "Loading H2H data..."
)


# IMPORTANT:
# Free Plan does not use last=10 here.
# Therefore only TWO arguments are sent.

h2h = get_h2h_summary(
    home_id,
    away_id
)


if not h2h["success"]:

    print()
    print("H2H ERROR:")
    print(h2h["error"])

else:

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

    print(
        "Home goals:",
        h2h["home_goals"]
    )

    print(
        "Away goals:",
        h2h["away_goals"]
    )


# ============================================================
# FINISHED
# ============================================================

print()
print("==============================================")
print("       FORM TEST FINISHED")
print("==============================================")
print()