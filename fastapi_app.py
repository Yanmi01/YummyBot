from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import graph_with_order_tools, OrderState, WELCOME_MSG

app = FastAPI()

# In-memory session storage (replace with DB in production)
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Initialize or get session
        if request.session_id not in sessions:
            sessions[request.session_id] = OrderState(
                messages=[], 
                order=[], 
                finished=False
            )
        
        state = sessions[request.session_id]
        
        # Process input
        state["messages"].append(("user", request.message))
        new_state = graph_with_order_tools.invoke(state)
        
        # Update session
        active_sessions[request.session_id] = new_state
        
        return {
            "response": new_state["messages"][-1].content,
            "order": new_state["order"]
        }
    except Exception as e:
        return {"error": str(e)}
