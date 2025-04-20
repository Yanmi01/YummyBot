from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import graph_with_order_tools, OrderState, WELCOME_MSG, process_human_input

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
        state = process_human_input(state, request.message)
        state = graph_with_order_tools.invoke(state)
        
        # Store updated state
        sessions[request.session_id] = state
        
        return {
            "response": state["messages"][-1].content,
            "order": state["order"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
