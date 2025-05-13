from fastapi import WebSocket
from motor.motor_asyncio import AsyncIOMotorClient
import os
from brokers.smart_websocket_client import SmartWebSocketV2Client  # Import your WebSocket client

from fastapi import FastAPI, Request, Form, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import SessionLocal
from models import Strategy

app = FastAPI()

# mount templates and static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")  # optional


# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Railway injects this automatically
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["trading"]
collection = db["market_data"]

# Initialize WebSocket Client
ws_client = SmartWebSocketV2Client(MONGO_URI)

# Store connected WebSocket clients
active_connections = set()

@app.on_event("startup")
async def startup_event():
    print("Starting WebSocket Client...")
    # Start WebSocket connection (implement connection logic in the class)
    # Example: await ws_client.start() (if async)

@app.get("/latest-data")
async def get_latest_data():
    """Returns the most recent market data"""
    data = await collection.find_one({}, sort=[("_id", -1)])
    if data:
        data["_id"] = str(data["_id"])  # Convert ObjectId to string
        return data
    return {"message": "No data available"}

@app.get("/strategies", response_class=HTMLResponse)
def list_strategies(request: Request, db: Session = Depends(get_db)):
    strategies = db.query(Strategy).all()
    return templates.TemplateResponse("strategy_list.html", {
        "request": request,
        "strategies": strategies
    })


@app.post("/submit-strategy", response_class=HTMLResponse)
def submit_strategy(
    request: Request,
    db: Session = Depends(get_db),
    symbol: str = Form(...),
    instrument_type: str = Form(...),
    exchange: str = Form(""),
    expiry: str = Form(""),
    entry_criteria: str = Form(""),
    exit_criteria: str = Form(""),
    indicators_used: str = Form(""),
    timeframe: str = Form(...),
    capital_allocation: float = Form(0),
    position_size: int = Form(0),
    stop_loss: float = Form(0),
    take_profit: float = Form(0),
    execution_mode: str = Form(...),
    api_key: str = Form(""),
    order_type: str = Form(...),
    notification_email: str = Form(""),
    benchmark_symbol: str = Form(""),
    transaction_cost: float = Form(0),
):
    strategy = Strategy(
        symbol=symbol,
        instrument_type=instrument_type,
        exchange=exchange,
        expiry=expiry,
        entry_criteria=entry_criteria,
        exit_criteria=exit_criteria,
        indicators_used=indicators_used,
        timeframe=timeframe,
        capital_allocation=capital_allocation,
        position_size=position_size,
        stop_loss=stop_loss,
        take_profit=take_profit,
        execution_mode=execution_mode,
        api_key=api_key,
        order_type=order_type,
        notification_email=notification_email,
        benchmark_symbol=benchmark_symbol,
        transaction_cost=transaction_cost
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    return templates.TemplateResponse("strategy_form.html", {"request": request, "submitted": True})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time data streaming"""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received: {message}")
            await websocket.send_text(f"Echo: {message}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        active_connections.remove(websocket)

async def broadcast_message(data):
    """Send real-time updates to all WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            print(f"Error sending to client: {e}")

# Modify WebSocket Client to push data to connected clients
async def on_message(message):
    """When new market data arrives, send it to WebSocket clients"""
    data = {"message": message}
    await collection.insert_one(data)  # Save to MongoDB
    await broadcast_message(data)  # Send to WebSocket clients

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Attach the custom function to SmartWebSocketV2Client
ws_client.on_message = on_message
