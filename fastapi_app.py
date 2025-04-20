from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import graph_with_order_tools, OrderState, WELCOME_MSG

app = FastAPI()

# Session storage (in-memory for now)
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.on_event("startup")
async def initialize_bot():
    """Warm up the graph on startup"""
    try:
        # Initialize with welcome message
        dummy_state = OrderState(
            messages=[("assistant", WELCOME_MSG)],
            order=[],
            finished=False
        )
        graph_with_order_tools.invoke(dummy_state)
    except Exception as e:
        print(f"Startup initialization failed: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        # Initialize or get session
        if request.session_id not in sessions:
            sessions[request.session_id] = OrderState(
                messages=[("assistant", WELCOME_MSG)],  # Start with welcome
                order=[],
                finished=False
            )
        
        state = sessions[request.session_id]
        
        # Add user message
        state["messages"].append(("user", request.message))
        
        # Process through graph
        new_state = graph_with_order_tools.invoke(state)
        
        # Update session
        sessions[request.session_id] = new_state
        
        # Get last AI response
        ai_responses = [msg for msg in new_state["messages"] 
                       if isinstance(msg, tuple) and msg[0] == "assistant"]
        last_response = ai_responses[-1][1] if ai_responses else WELCOME_MSG
        
        return {
            "response": last_response,
            "order": new_state["order"],
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint for health checks"""
    return {"status": "OK", "message": "YummyBot is ready"}
