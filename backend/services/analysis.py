import math

def poisson(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def matrix(lam_home, lam_away, max_goals=9):
    return [[poisson(i, lam_home) * poisson(j, lam_away)
             for j in range(max_goals + 1)]
            for i in range(max_goals + 1)]

def pct(x):
    return round(max(0, min(1, x)) * 100, 1)

def markets(m):
    n = len(m)
    home = sum(m[i][j] for i in range(n) for j in range(n) if i > j)
    draw = sum(m[i][j] for i in range(n) for j in range(n) if i == j)
    away = sum(m[i][j] for i in range(n) for j in range(n) if i < j)

    def over(threshold):
        return sum(m[i][j] for i in range(n) for j in range(n)
                   if i + j > threshold)

    btts = sum(m[i][j] for i in range(1,n) for j in range(1,n))
    scores = sorted(
        ((i, j, m[i][j]) for i in range(n) for j in range(n)),
        key=lambda x: x[2], reverse=True
    )[:5]

    return {
        "1N2": {"1": pct(home), "N": pct(draw), "2": pct(away)},
        "doubleChance": {
            "1N": pct(home + draw),
            "N2": pct(draw + away),
            "12": pct(home + away)
        },
        "BTTS": {"yes": pct(btts), "no": pct(1-btts)},
        "overUnder": {
            "over1.5": pct(over(1.5)),
            "over2.5": pct(over(2.5)),
            "over3.5": pct(over(3.5))
        },
        "topScores": [
            {"score": f"{i}-{j}", "probability": pct(p)}
            for i,j,p in scores
        ]
    }

def estimate_lambdas(match):
    # Valeurs de secours. Elles seront remplacées par les moyennes
    # des historiques dès que ceux-ci sont disponibles.
    return 1.35, 1.05

def analyze_match(client, match):
    home = next((p for p in match.get("participants", [])
                 if p.get("meta", {}).get("location") == "home"), {})
    away = next((p for p in match.get("participants", [])
                 if p.get("meta", {}).get("location") == "away"), {})

    home_id, away_id = home.get("id"), away.get("id")
    lam_home, lam_away = estimate_lambdas(match)
    result = markets(matrix(lam_home, lam_away))

    return {
        "match": {
            "home": home.get("name", "Domicile"),
            "away": away.get("name", "Extérieur"),
            "homeId": home_id,
            "awayId": away_id,
            "league": (match.get("league") or {}).get("name")
        },
        "expectedGoals": {
            "home": round(lam_home, 2),
            "away": round(lam_away, 2),
            "total": round(lam_home + lam_away, 2)
        },
        **result,
        "status": "basic_poisson",
        "note": "Les historiques détaillés doivent être reliés aux endpoints SportMonks avant production."
    }
