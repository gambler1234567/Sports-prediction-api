from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

# --- YOUR API KEY (DO NOT REMOVE) ---
API_KEY = 'fd80eb591b9b059e2fd4ff82d27a4eff'
BANKROLL = 1000.0 

# NEW: Fast-Test Endpoint to check server speed
@app.get("/fast-test")
def fast_test():
    return {"status": "fast", "message": "Brain is working instantly!"}

@app.get("/")
def home():
    return {"message": "Server is ONLINE. Go to /predict?sport=americanfootball_nfl"}

@app.get("/predict")
def get_prediction(sport: str = "americanfootball_nfl"):
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    
    try:
        # This part reaches out to the internet, which takes 1-2 seconds
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

    results = []
    # If the API returned a list of games
    if isinstance(data, list):
        for match in data[:10]:
            home_t = match['home_team']
            away_t = match['away_team']
            
            # --- VEGAS TRAP & KELLY MATH ---
            is_trap = True # Simplified trap flag
            h_score = 24.5 if "nfl" in sport else 110.2
            a_score = 21.8 if "nfl" in sport else 108.5
            
            try:
                odds = match['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                win_prob = 0.58 
                b = odds - 1
                kelly_f = ((b * win_prob) - (1 - win_prob)) / b
                suggested_bet = max(0, kelly_f * BANKROLL * 0.5)
            except:
                odds, suggested_bet = 0, 0

            results.append({
                "game": f"{home_t} vs {away_t}",
                "prediction": f"{h_score} - {a_score}",
                "vegas_trap": is_trap,
                "bet_amount": f"${suggested_bet:.2f}"
            })
    
    return {"status": "success", "sport": sport, "picks": results}

# --- SERVER STARTUP (DO NOT REMOVE) ---
if __name__ == "__main__":
    print("Starting server... Ready for local testing.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
