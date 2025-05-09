## 📐 Why This Layout Follows SOLID Principles

| Principle                 | Applied Design Practice |
|--------------------------|-------------------------|
| **S - Single Responsibility** | Each module handles one responsibility:<br>• `websocket_client.py` manages only the WebSocket lifecycle<br>• Observers handle specific data reactions like EMA, order placement, or charting |
| **O - Open/Closed**         | System behavior is configurable via YAML and observers — add new observers without modifying existing code |
| **L - Liskov Substitution** | All observers implement a uniform `update(data)` interface, allowing clean substitution of behavior |
| **I - Interface Segregation** | Components depend only on what they use:<br>• YAML defines configuration contracts<br>• CLI and API interact through clean boundaries |
| **D - Dependency Inversion** | High-level modules (CLI/API) depend on abstractions (observer interface, YAML config), not low-level concrete implementations |
