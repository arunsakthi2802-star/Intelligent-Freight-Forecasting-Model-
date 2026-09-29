import asyncio
import websockets
import json
import os
import pandas as pd
from datetime import datetime

API_KEY = "0a8aa200af2507ac4a3729e07e9d201d393bfc84"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LIVE_FILE = os.path.join(DATA_DIR, "demo", "vessels_live.json")

# Dictionary to store the latest state of vessels
vessels_state = {}

async def connect_ais_stream():
    url = "wss://stream.aisstream.io/v0/stream"
    
    # We will subscribe to a global bounding box, but filter for certain MMSIs or just take whatever comes first
    # To prevent flooding, we will only track a limited number of ships (e.g. 100)
    subscribe_message = {
        "APIKey": API_KEY,
        "BoundingBoxes": [[[-90, -180], [90, 180]]] # Global coverage
    }

    print("Connecting to aisstream.io...")
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps(subscribe_message))
                print("Connected and subscribed to AISStream.")
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    msg_type = data.get("MessageType")
                    
                    if msg_type == "ShipStaticData":
                        static = data.get("Message", {}).get("ShipStaticData", {})
                        mmsi = str(static.get("UserID"))
                        dest = static.get("Destination", "").strip()
                        if mmsi in vessels_state and dest:
                            vessels_state[mmsi]["destination"] = dest

                    elif msg_type == "PositionReport":
                        report = data.get("Message", {}).get("PositionReport", {})
                        meta = data.get("MetaData", {})
                        
                        mmsi = str(report.get("UserID"))
                        lat = report.get("Latitude")
                        lon = report.get("Longitude")
                        ship_name = meta.get("ShipName", "").strip() or f"Unknown ({mmsi})"
                        
                        if lat and lon and lat <= 90 and lon <= 180:
                            if mmsi not in vessels_state:
                                vessels_state[mmsi] = {
                                    "mmsi": mmsi,
                                    "name": ship_name,
                                    "class": "CARGO" if "CARGO" in ship_name.upper() else "UNKNOWN",
                                    "dwt": 50000 + (hash(mmsi) % 100000), # pseudo-random DWT
                                    "cost_per_tonne": 12.0 + (hash(mmsi) % 15), # pseudo-random cost 12-27
                                    "destination": "UNKNOWN",
                                    "history": [] 
                                }
                            
                            # Add current position to history
                            history = vessels_state[mmsi]["history"]
                            if not history or history[-1] != [lon, lat]:
                                history.append([lon, lat])
                                if len(history) > 20:
                                    history.pop(0)
                            
                            # If geographically near India, force an Indian destination for the demo scenario
                            dest = vessels_state[mmsi].get("destination", "UNKNOWN")
                            if 5 <= lat <= 25 and 65 <= lon <= 90 and dest == "UNKNOWN":
                                dest = "MUMBAI (IN)" if lon < 75 else "CHENNAI (IN)"
                            
                            vessels_state[mmsi].update({
                                "lat": lat,
                                "lon": lon,
                                "speed": report.get("Sog", 0),
                                "heading": report.get("TrueHeading", 0),
                                "destination": dest,
                                "last_updated": datetime.now().isoformat()
                            })
                            
                            if len(vessels_state) > 100:
                                vessels_state.pop(next(iter(vessels_state)))
                                
                            if sum(len(v['history']) for v in vessels_state.values()) % 10 == 0:
                                with open(LIVE_FILE, "w") as f:
                                    json.dump(list(vessels_state.values()), f)
                                    
        except Exception as e:
            print(f"AISStream Connection Error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())
