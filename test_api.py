from football_api import get_today_fixtures


print()
print("================================")
print("      HARMON AI PREDICTOR")
print("================================")
print()


result = get_today_fixtures()


if not result["success"]:

    print("API ERROR:")
    print(result["error"])


else:

    data = result["data"]


    print(
        "Matches found:",
        data.get(
            "results",
            0
        )
    )


    print()
    print("--------------------------------")


    for fixture in data.get(
        "response",
        []
    ):


        league = fixture[
            "league"
        ][
            "name"
        ]


        country = fixture[
            "league"
        ][
            "country"
        ]


        home = fixture[
            "teams"
        ][
            "home"
        ][
            "name"
        ]


        away = fixture[
            "teams"
        ][
            "away"
        ][
            "name"
        ]


        fixture_id = fixture[
            "fixture"
        ][
            "id"
        ]


        status = fixture[
            "fixture"
        ][
            "status"
        ][
            "short"
        ]


        print()

        print(
            f"{home} vs {away}"
        )

        print(
            f"League: {league}"
        )

        print(
            f"Country: {country}"
        )

        print(
            f"Fixture ID: {fixture_id}"
        )

        print(
            f"Status: {status}"
        )


        print(
            "--------------------------------"
        )
        print()
print("=" * 50)
print("TEST TEAM RECENT FIXTURES")
print("=" * 50)

from football_api import get_team_last_fixtures

# Arsenal ID kwenye API-Football
team_id = 42

result = get_team_last_fixtures(
    team_id,
    10
)

print()
print("Success:", result.get("success"))

if result.get("success"):

    matches = result["data"].get(
        "response",
        []
    )

    print("Matches found:", len(matches))

    for match in matches:

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        status = match["fixture"]["status"]["short"]

        print(
            f"{home} vs {away} | {status}"
        )

else:

    print(
        "ERROR:",
        result.get("error")
    )