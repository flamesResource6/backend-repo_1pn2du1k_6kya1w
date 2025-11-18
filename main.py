import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EventIn(BaseModel):
    title: str
    date: str
    venue: str
    description: str
    image: str
    price: float
    tickets_available: int

class OrderIn(BaseModel):
    event_id: str
    name: str
    email: str
    quantity: int


@app.get("/")
def read_root():
    return {"message": "Events API running"}


@app.get("/api/events")
def list_events(limit: int = 20):
    try:
        events = get_documents("event", {}, limit)
        # Convert ObjectId to string
        for e in events:
            e["_id"] = str(e.get("_id"))
        return {"events": events}
    except Exception as e:
        return {"events": sample_events()[:limit], "database": "unavailable", "error": str(e)[:100]}


@app.post("/api/orders")
def create_order(order: OrderIn):
    # Basic validation
    if order.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    # Try to fetch event to compute total and validate availability
    try:
        ev = db["event"].find_one({"_id": ObjectId(order.event_id)}) if db else None
    except Exception:
        ev = None

    if ev:
        if ev.get("tickets_available", 0) < order.quantity:
            raise HTTPException(status_code=400, detail="Not enough tickets available")
        total = float(ev.get("price", 0)) * order.quantity
    else:
        # Fallback: search in sample
        ev = next((x for x in sample_events() if x["_id"] == order.event_id), None)
        total = float(ev["price"]) * order.quantity if ev else 0

    doc = {
        "event_id": order.event_id,
        "name": order.name,
        "email": order.email,
        "quantity": order.quantity,
        "total_amount": total,
        "status": "confirmed" if total > 0 else "pending",
    }

    try:
        oid = create_document("order", doc)
        return {"order_id": oid, "status": doc["status"], "total_amount": total}
    except Exception:
        # allow creating even if db unavailable (demo)
        return {"order_id": "demo", "status": doc["status"], "total_amount": total}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


def sample_events():
    return [
        {
            "_id": "000000000000000000000001",
            "title": "Neon Nights Festival",
            "date": "2025-12-01",
            "venue": "HoloDome Arena",
            "description": "Step into a glow-soaked world of immersive sound and light.",
            "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1600&auto=format&fit=crop",
            "price": 79.0,
            "tickets_available": 250,
        },
        {
            "_id": "000000000000000000000002",
            "title": "Quantum Comedy Night",
            "date": "2025-11-08",
            "venue": "The Laugh Matrix",
            "description": "Stand-up from the future that will split your sides across timelines.",
            "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1600&auto=format&fit=crop",
            "price": 39.0,
            "tickets_available": 120,
        },
        {
            "_id": "000000000000000000000003",
            "title": "Synthwave Symphony",
            "date": "2026-01-20",
            "venue": "Aurora Concert Hall",
            "description": "An orchestral journey through retro-future soundscapes.",
            "image": "https://images.unsplash.com/photo-1545235617-7a424c1a60cc?q=80&w=1600&auto=format&fit=crop",
            "price": 99.0,
            "tickets_available": 80,
        },
    ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
