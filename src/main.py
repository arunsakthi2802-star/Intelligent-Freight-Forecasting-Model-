from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import uvicorn

from .schemas import VoyageRequest
from .services import process_voyage_request

app = FastAPI(title="SIH26006 Voyage Optimization Engine", version="2.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to SIH26006 Voyage Optimization Engine API. See /docs for endpoints."}

@app.post("/planning/voyage")
def plan_voyage(request: VoyageRequest):
    return process_voyage_request(request)

@app.post("/planning/vessel-availability")
def vessel_availability(request: VoyageRequest):
    res = process_voyage_request(request)
    return {"candidate_vessels": res["candidate_vessels"]}

@app.post("/planning/low-cost-vessels")
def low_cost_vessels(request: VoyageRequest):
    res = process_voyage_request(request)
    return {"low_cost_vessels": res["low_cost_vessels"]}

@app.get("/map", response_class=HTMLResponse)
def get_map():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SIH26006 Vessel Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            #map { height: 600px; width: 100%; }
            body { font-family: Arial, sans-serif; }
        </style>
    </head>
    <body>
        <h2>Live Vessel Tracker & Optimizer</h2>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([20.0, 80.0], 4);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            
            // Dummy data for demo
            var vessels = [
                {name: "Ocean King", lat: 15.0, lon: 75.0, status: "CONFIRMED_AVAILABLE", cost: 550000},
                {name: "Sea Wave", lat: 5.0, lon: 85.0, status: "EN_ROUTE", cost: 720000},
                {name: "Pacific Star", lat: -10.0, lon: 110.0, status: "OPERATIONALLY_AVAILABLE", cost: 480000}
            ];
            
            vessels.forEach(function(v) {
                var color = v.status === "CONFIRMED_AVAILABLE" ? "green" : (v.status === "EN_ROUTE" ? "blue" : "orange");
                var circle = L.circleMarker([v.lat, v.lon], {
                    color: color,
                    radius: 8
                }).addTo(map);
                circle.bindPopup("<b>" + v.name + "</b><br>Status: " + v.status + "<br>Est Cost: $" + v.cost);
            });
            
            // Route to Paradip
            var latlngs = [
                [-10.0, 110.0],
                [5.0, 95.0],
                [20.26, 86.67] // Paradip
            ];
            var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
            map.fitBounds(polyline.getBounds());
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
