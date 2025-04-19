import gradio as gr
from typing import Dict, List
from main import graph_with_order_tools, OrderState, WELCOME_MSG

class GradioChatWrapper:
    def __init__(self):
        self.state = OrderState(messages=[], order=[], finished=False)
        self.history = []
        
    def process_user_input(self, user_input: str):
        # Update state with user message
        self.state["messages"] = [("user", user_input)]
        
        # Process through the graph
        self.state = graph_with_order_tools.invoke(self.state)
        
        # Get the last AI message
        last_msg = self.state["messages"][-1].content if self.state["messages"] else WELCOME_MSG
        
        # Update chat history
        self.history.append((user_input, last_msg))
        
        # Handle special cases (order confirmation, etc.)
        if "Your order:" in last_msg:
            # Format the order display
            order_text = "\n".join([f"• {item}" for item in self.state["order"]]) if self.state["order"] else "No items in order"
            last_msg = f"Your order:\n{order_text}\n\nIs this correct? (Please respond with 'yes' or any modifications)"
        
        return self.history, ""

# Create the Gradio interface
with gr.Blocks(title="YummyBot Food Ordering System") as demo:
    gr.Markdown("# 🍽️ YummyBot Food Ordering System")
    gr.Markdown("Welcome to our restaurant! Order your favorite Nigerian dishes.")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Order Conversation", height=500, type="messages")
            msg = gr.Textbox(label="Your message", placeholder="Type your order here...")
            clear = gr.ClearButton([msg, chatbot])
            
        with gr.Column(scale=1):
            gr.Markdown("### Menu Preview")
            menu_display = gr.Textbox(label="Current Menu", interactive=False, 
                                     value="Main Dishes: Amala, Eba, Fufu, Rice, Pounded Yam\n"
                                           "Stews: Egusi, Vegetable, Fried stew\n"
                                           "Proteins: Goat, Turkey, Chicken, Beef\n"
                                           "Sides: Plantain, Salad\n"
                                           "Drinks: Malt, Yoghurt, Coke, Fanta", 
                                     lines=10)
            
            order_status = gr.Textbox(label="Your Current Order", interactive=False, lines=5)
            place_order_btn = gr.Button("Place Order", variant="primary")

    # Initialize the chat wrapper
    chat_wrapper = GradioChatWrapper()
    
    def respond(message, chat_history):
        # Process the message
        chat_history, _ = chat_wrapper.process_user_input(message)
        
        # Update order status display
        current_order = "\n".join([f"• {item}" for item in chat_wrapper.state["order"]]) if chat_wrapper.state["order"] else "No items yet"
        
        return chat_history, "", current_order
    
    def place_order():
        # Simulate placing the order
        if not chat_wrapper.state["order"]:
            return "Please add items to your order first!", chat_wrapper.history
        
        # Process the order placement
        chat_wrapper.state["messages"] = [("user", "place order")]
        chat_wrapper.state = graph_with_order_tools.invoke(chat_wrapper.state)
        
        # Get the response
        response = chat_wrapper.state["messages"][-1].content
        
        # Update history
        chat_wrapper.history.append(("Place order", response))
        
        return response, chat_wrapper.history
    
    # Set up event handlers
    msg.submit(respond, [msg, chatbot], [chatbot, msg, order_status])
    place_order_btn.click(place_order, outputs=[order_status, chatbot])

# Launch the interface
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8000)