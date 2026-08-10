import logging
from datetime import datetime

logger = logging.getLogger("catalog_db")

CATALOG_DATA = {
    "rice": {"price": 50.0, "stock": 100},
    "wheat": {"price": 40.0, "stock": 200},
    "sugar": {"price": 45.0, "stock": 50},
    "salt": {"price": 20.0, "stock": 500},
    "cooking oil": {"price": 120.0, "stock": 30},
    "milk": {"price": 30.0, "stock": 10},
}

def check_catalog_and_stock(items_requested: dict) -> dict:
    """
    Check the local commerce catalog for the requested items and compute the total.
    items_requested should be a dictionary of item names to requested quantities.
    Example: {"rice": 2, "sugar": 1}
    """
    try:
        total_cost = 0.0
        available_items = []
        out_of_stock_items = []
        unavailable_items = []
        
        for item, qty in items_requested.items():
            item_lower = item.lower()
            if item_lower in CATALOG_DATA:
                stock = CATALOG_DATA[item_lower]["stock"]
                price = CATALOG_DATA[item_lower]["price"]
                
                if stock >= qty:
                    cost = price * qty
                    total_cost += cost
                    available_items.append({"item": item_lower, "quantity": qty, "cost": cost})
                elif stock > 0:
                    cost = price * stock
                    total_cost += cost
                    available_items.append({"item": item_lower, "quantity": stock, "cost": cost, "note": f"Only {stock} available"})
                    out_of_stock_items.append(f"{item_lower} (short by {qty - stock})")
                else:
                    out_of_stock_items.append(item_lower)
            else:
                unavailable_items.append(item_lower)
                
        # Generate the date when data is from
        today = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "status": "success",
            "data_as_of": today,
            "available_items": available_items,
            "out_of_stock_items": out_of_stock_items,
            "unavailable_items": unavailable_items,
            "total_cost": total_cost
        }
    except Exception as e:
        logger.error(f"Error checking catalog and stock: {e}")
        return {
            "status": "error",
            "message": "The catalog database is currently unavailable. Please try again later."
        }
