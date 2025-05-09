# 🚀 Installation Guide for Algomin

This guide explains how to set up and run the **Algomin** project locally, including the CLI, FastAPI server, and WebSocket-based data stream observers.

---

## 📦 1. Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **Git**
- **pip** (or optionally [Poetry](https://python-poetry.org/))
- A valid **AngelOne developer account** (for WebSocket access)

---

## 📁 2. Clone the Repository

```bash
git clone https://github.com/yourusername/algomin.git
cd algomin


python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

```

```commandline


cd ~/Documents/GitHub/algomin
source .algomin/bin/activate
cd base/
pip install -e .
cd ../live/
pip install -e .
cd src/live

```


```commandline

Configure YAML Parameters
Update the YAML configuration located at:

config/common.yaml
Here’s an example:

websocket:
  mode: full
  correlation_id: sub_001
  subscriptions:
    - "26000"

limit_orders:
  - tradingsymbol: RELIANCE-EQ
    symbol_token: "26000"
    quantity: 1
    price: 95.0

```


```run_client.py

Running the Project
▶️ Run the CLI
To run using CLI configuration (YAML):

bash
Copy
Edit
python cli/run_client.py

```


```uvicorn
Run the FastAPI Server

uvicorn main:app --reload

Then open your browser at http://localhost:8000

Available endpoints:

GET /start – starts the WebSocket client in a thread
GET /stop – stops the WebSocket client
WS /ws/stream – (optional) real-time frontend WebSocket endpoint


```


```commandline

Run Tests
To run all unit tests:

pytest tests/

```

```
📎 Notes
All live data processing logic is handled via observers in observers/.

Configuration is decoupled via YAML to support both CLI and frontend usage.

For frontend integration ideas, see frontend/README.md.

```