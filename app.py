from flask import Flask, request, render_template
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import markdown

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Groq/Llama3 model
try:
    llm = ChatOpenAI(
        model_name="llama3-70b-8192",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=1024
    )
    print("LLM initialized successfully!")
except Exception as e:
    print(f"Initialization error: {e}")
    llm = None  # Ensure we have a fallback
    
@app.route('/', methods=['GET', 'POST'])
def home():
    response = None
    if request.method == 'POST' and llm:
        query = request.form['query']
        try:
            # Get the raw response
            raw_response = llm.invoke(query).content
            
            # Convert Markdown to HTML and preserve line breaks
            formatted_response = markdown.markdown(raw_response)
            
        except Exception as e:
            formatted_response = f"Error: {str(e)}"
            
    return render_template('index.html', 
                         response=formatted_response if 'formatted_response' in locals() else None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
