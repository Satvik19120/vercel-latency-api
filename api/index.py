from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],  # Allow only POST
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load data once at startup
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"
df = pd.read_json(DATA_FILE)

@app.get("/")
async def root():
    return {"message": "Vercel Latency Analytics API is running."}

@app.post("/api/")
async def latency_stats(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 200)  # Default if not given

    results = []
    for region in regions:
        region_df = df[df["region"] == region]
        if not region_df.empty:
            avg_latency = float(region_df["latency_ms"].mean())
            p95_latency = float(np.percentile(region_df["latency_ms"], 95))
            avg_uptime = float(region_df["uptime_pct"].mean())
            breaches = int((region_df["latency_ms"] > threshold).sum())
            results.append({
                "region": region,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            })
        else:
            # Return nulls if region not found
            results.append({
                "region": region,
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            })
    return {"regions": results}
