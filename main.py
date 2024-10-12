from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os 

app = FastAPI(title="Inventory and Clock-In System")

from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.inventory_system


# print (MONGO_URL)

class ItemBase(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: str

class Item(ItemBase):
    id: str
    insert_date: datetime

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ClockInBase(BaseModel):
    email: EmailStr
    location: str

class ClockIn(ClockInBase):
    id: str
    insert_datetime: datetime

class ClockInCreate(ClockInBase):
    pass

class ClockInUpdate(ClockInBase):
    pass

# Helper functions
def item_helper(item) -> Item:
    return Item(
        id=str(item["_id"]),
        name=item["name"],
        email=item["email"],
        item_name=item["item_name"],
        quantity=item["quantity"],
        expiry_date=item["expiry_date"],
        insert_date=item["insert_date"]
    )

def clock_in_helper(record) -> ClockIn:
    return ClockIn(
        id=str(record["_id"]),
        email=record["email"],
        location=record["location"],
        insert_datetime=record["insert_datetime"]
    )

# Item CRUD operations
@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = item.dict()
    new_item["insert_date"] = datetime.utcnow()
    result = await db.items.insert_one(new_item)
    created_item = await db.items.find_one({"_id": result.inserted_id})
    return item_helper(created_item)

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if item:
        return item_helper(item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/items/filter", response_model=List[Item])
async def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[str] = None,
    insert_date: Optional[str] = None,
    quantity: Optional[int] = None
):
    query = {}
    if email:
        query["email"] = email
    if expiry_date:
        query["expiry_date"] = {"$gte": expiry_date}
    if insert_date:
        query["insert_date"] = {"$gte": datetime.fromisoformat(insert_date)}
    if quantity:
        query["quantity"] = {"$gte": quantity}

    items = await db.items.find(query).to_list(1000)
    return [item_helper(item) for item in items]

@app.get("/items/aggregate")
async def aggregate_items():
    pipeline = [
        {"$group": {"_id": "$email", "count": {"$sum": 1}}}
    ]
    result = await db.items.aggregate(pipeline).to_list(1000)
    return result

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db.items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemUpdate):
    updated_item = item.dict(exclude_unset=True)
    result = await db.items.update_one({"_id": ObjectId(item_id)}, {"$set": updated_item})
    if result.modified_count == 1:
        updated_doc = await db.items.find_one({"_id": ObjectId(item_id)})
        return item_helper(updated_doc)
    raise HTTPException(status_code=404, detail="Item not found")

# Clock-In CRUD operations
@app.post("/clock-in", response_model=ClockIn)
async def create_clock_in(clock_in: ClockInCreate):
    new_clock_in = clock_in.dict()
    new_clock_in["insert_datetime"] = datetime.utcnow()
    result = await db.clock_in.insert_one(new_clock_in)
    created_clock_in = await db.clock_in.find_one({"_id": result.inserted_id})
    return clock_in_helper(created_clock_in)

@app.get("/clock-in/{record_id}", response_model=ClockIn)
async def get_clock_in(record_id: str):
    record = await db.clock_in.find_one({"_id": ObjectId(record_id)})
    if record:
        return clock_in_helper(record)
    raise HTTPException(status_code=404, detail="Clock-in record not found")

@app.get("/clock-in/filter", response_model=List[ClockIn])
async def filter_clock_in(
    email: Optional[str] = None,
    location: Optional[str] = None,
    insert_datetime: Optional[str] = None
):
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = {"$gte": datetime.fromisoformat(insert_datetime)}

    records = await db.clock_in.find(query).to_list(1000)
    return [clock_in_helper(record) for record in records]

@app.delete("/clock-in/{record_id}")
async def delete_clock_in(record_id: str):
    result = await db.clock_in.delete_one({"_id": ObjectId(record_id)})
    if result.deleted_count == 1:
        return {"message": "Clock-in record deleted successfully"}
    raise HTTPException(status_code=404, detail="Clock-in record not found")

@app.put("/clock-in/{record_id}", response_model=ClockIn)
async def update_clock_in(record_id: str, clock_in: ClockInUpdate):
    updated_clock_in = clock_in.dict(exclude_unset=True)
    result = await db.clock_in.update_one({"_id": ObjectId(record_id)}, {"$set": updated_clock_in})
    if result.modified_count == 1:
        updated_doc = await db.clock_in.find_one({"_id": ObjectId(record_id)})
        return clock_in_helper(updated_doc)
    raise HTTPException(status_code=404, detail="Clock-in record not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)