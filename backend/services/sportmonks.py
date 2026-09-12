import requests

BASE_URL = "https://api.sportmonks.com/v3/football"

class SportMonksClient:
    def __init__(self, token):
        self.token = token

    def _get(self, path, params=None):
        if not self.token:
            raise RuntimeError("SPORTMONKS_TOKEN non configuré")
        params = dict(params or {})
        params["api_token"] = self.token
        r = requests.get(f"{BASE_URL}/{path.lstrip('/')}", params=params, timeout=25)
        r.raise_for_status()
        return r.json()

    def fixtures_by_date(self, date):
        if not date:
            raise ValueError("Le paramètre date est obligatoire (YYYY-MM-DD)")
        data = self._get(f"fixtures/date/{date}", {
            "include": "participants;league"
        })
        return self._normalize_fixture_list(data)

    def fixture_details(self, fixture_id):
        data = self._get(f"fixtures/{fixture_id}", {
            "include": "participants;league;statistics;events"
        })
        return data.get("data", data)

    def team_fixtures(self, team_id, page=1):
        data = self._get(f"teams/{team_id}/fixtures", {
            "include": "participants;league",
            "page": page
        })
        return data.get("data", [])

    def head_to_head(self, team_a, team_b):
        data = self._get(f"fixtures/head-to-head/{team_a}/{team_b}", {
            "include": "participants;league"
        })
        return data.get("data", [])

    def _normalize_fixture_list(self, data):
        rows = data.get("data", [])
        result = []
        for f in rows:
            participants = f.get("participants", [])
            home = next((p for p in participants if p.get("meta", {}).get("location") == "home"), None)
            away = next((p for p in participants if p.get("meta", {}).get("location") == "away"), None)
            result.append({
                "id": f.get("id"),
                "starting_at": f.get("starting_at"),
                "league": (f.get("league") or {}).get("name"),
                "home": (home or {}).get("name", "Domicile"),
                "away": (away or {}).get("name", "Extérieur"),
                "home_id": (home or {}).get("id"),
                "away_id": (away or {}).get("id"),
            })
        return {"ok": True, "date": data.get("meta", {}).get("date"), "fixtures": result}
