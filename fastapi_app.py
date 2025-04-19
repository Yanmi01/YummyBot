from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from main import graph_with_order_tools, OrderState, WELCOME_MSG

app = FastAPI()

# State storage (replace with Redis in production)
active_sessions = {}

class UserInput(BaseModel):
    message: str
    session_id: str = "default"  # For multi-user support

@app.post("/chat")
async def chat(user_input: UserInput):
    """Handle all YummyBot interactions"""
    try:
        # Initialize or retrieve session
        if user_input.session_id not in active_sessions:
            active_sessions[user_input.session_id] = OrderState(
                messages=[], order=[], finished=False
            )
        
        state = active_sessions[user_input.session_id]
        
        # Process input
        state["messages"].append(("user", user_input.message))
        new_state = graph_with_order_tools.invoke(state)
        
        # Update session
        active_sessions[user_input.session_id] = new_state
        
        return {
            "response": new_state["messages"][-1].content,
            "order": new_state["order"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tool-specific endpoints (optional but recommended)
@app.post("/add_to_order")
async def add_item(food: str, session_id: str):
    """Direct API for adding items"""
    # ... implement using graph_with_order_tools ...

@app.get("/get_order")
async def get_order(session_id: str):
    """Check current order"""
    if session_id in active_sessions:
        return active_sessions[session_id]["order"]
    return []

# Keep your existing web interface
@app.get("/", response_class=HTMLResponse)
async def web_interface():
    return """<html>...</html>"""