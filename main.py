# main.py
import os
import requests
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("API_KEY", "CG-5tut4FcZjyF6hsWidKxHHXrG")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

def get_api_key(
    x_cg_demo_api_key: str = Header(None, alias="x-cg-demo-api-key"),
    x_cg_demo_api_key_query: str = Query(None, alias="x_cg_demo_api_key")
):
    """
    Retrieve the API key from either the header or the query parameter.
    Priority is given to the header.
    """
    # Check header first, then query string
    api_key = x_cg_demo_api_key or x_cg_demo_api_key_query
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Initialize the FastAPI application
app = FastAPI(
    title="Crypto Market Updates API",
    version="1.0.0",
    description="Fetch cryptocurrency market data using the CoinGecko API."
)

# Enable CORS (adjust for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint: List coins with market data (paginated)
@app.get("/v1/coins", dependencies=[Depends(get_api_key)], tags=["Coins"])
def list_coins(
    page_num: int = Query(1, alias="page_num", ge=1),
    per_page: int = Query(10, alias="per_page", ge=1)
):
    params = {
        "vs_currency": "cad",
        "order": "market_cap_desc",
        "page": page_num,
        "per_page": per_page,
        "sparkline": "false"
    }
    response = requests.get(f"{COINGECKO_BASE_URL}/coins/markets", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching coins data")
    return response.json()

# Endpoint: List coin categories (paginated)
@app.get("/v1/categories", dependencies=[Depends(get_api_key)], tags=["Categories"])
def list_categories(
    page_num: int = Query(1, alias="page_num", ge=1),
    per_page: int = Query(10, alias="per_page", ge=1)
):
    response = requests.get(f"{COINGECKO_BASE_URL}/coins/categories")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching categories")
    
    categories = response.json()
    # Perform manual pagination since the external API does not support it
    start = (page_num - 1) * per_page
    end = start + per_page
    return categories[start:end]

# Endpoint: Get details for a specific coin by coin_id
@app.get("/v1/coins/{coin_id}", dependencies=[Depends(get_api_key)], tags=["Coins"])
def get_coin(coin_id: str):
    params = {
        "vs_currency": "cad",
        "ids": coin_id,
        "order": "market_cap_desc",
        "sparkline": "false"
    }
    response = requests.get(f"{COINGECKO_BASE_URL}/coins/markets", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching coin details")
    data = response.json()
    if not data:
        raise HTTPException(status_code=404, detail="Coin not found")
    return data[0]

# Endpoint: Health check (validates both the app and CoinGecko API connectivity)
@app.get("/v1/health", tags=["Health"])
def health_check(api_key: str = Depends(get_api_key)):
    try:
        response = requests.get(f"{COINGECKO_BASE_URL}/ping", timeout=5)
        third_party_status = "ok" if response.status_code == 200 else "unreachable"
    except Exception:
        third_party_status = "unreachable"
    return {"status": "ok", "coingecko": third_party_status}

# Endpoint: Version information
@app.get("/v1/version", tags=["Version"])
def version_info():
    return {"version": "1.0.0", "description": "Crypto Market Updates API"}

# Optional: If you want to run the application directly with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)