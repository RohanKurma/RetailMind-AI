from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from shoppinggpt.router.lib_semantic_router import (
    SemanticRouter,
    PRODUCT_ROUTE_NAME,
    CHITCHAT_ROUTE_NAME
)
from shoppinggpt.chain import create_chitchat_chain
from shoppinggpt.agent import ShoppingAgent

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LLM and Embedding setup
LLM = ChatGoogleGenerativeAI(temperature=0, model="gemini-1.5-flash")

# Memory setup
SHARED_MEMORY = ConversationBufferMemory(return_messages=True)

# Initialize SemanticRouter
SEMANTIC_ROUTER = SemanticRouter()

app = Flask(__name__)

def handle_query(query: str) -> dict:
    """Handle user query and return response."""
    guided_route = SEMANTIC_ROUTER.guide(query)
    
    if guided_route == CHITCHAT_ROUTE_NAME:
        chitchat_chain = create_chitchat_chain(LLM, SHARED_MEMORY)
        response = chitchat_chain.invoke({"input": query})
    elif guided_route == PRODUCT_ROUTE_NAME:
        agent = ShoppingAgent(LLM, SHARED_MEMORY)
        response = agent.invoke(query)
    else:
        response = "Unknown query type"
    
    # Get content from response
    content = (
        response.content if hasattr(response, 'content')
        else response['output'] if isinstance(response, dict) and 'output' in response
        else str(response)
    )
    
    # Update shared memory
    SHARED_MEMORY.chat_memory.add_user_message(query)
    SHARED_MEMORY.chat_memory.add_ai_message(content)
    
    return {
        'response': content,
        'type': guided_route
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['GET'])
def get_bot_response():
    user_message = (request.args.get('msg') or '').strip()
    if not user_message:
        return jsonify({'error': 'Provide a non-empty msg parameter.'}), 400
    if len(user_message) > 2000:
        return jsonify({'error': 'Message exceeds 2000 characters.'}), 400
    response = handle_query(user_message)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1', host='127.0.0.1', port=int(os.getenv('PORT', '5000')))
