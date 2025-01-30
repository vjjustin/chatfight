from flask import Flask, request, render_template, jsonify
import threading
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os, re
import markdown

app = Flask(__name__)
load_dotenv()


def get_response(model_name, query, max_tokens):
    try:
        # Initialize fresh model on each request
        model = ChatOpenAI(
            model_name=model_name,
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
            max_tokens=512,  # Set during initialization
            max_completion_tokens=512
        )
        response = model.invoke(query).content
        return markdown.markdown(response)
    except Exception as e:
        return f"Error: {str(e)}"
        

def extract_and_fix_think_content(response_str):
    try:
        parts = response_str.split("</think>", 1)  # Split at first </think>

        if len(parts) >= 2:
            think_content = parts[0].split("<think>", 1)[-1].strip()  # Extract inside <think>
            answer_content = parts[1].strip()  # Everything after </think>

            # Ensure <p> tags are balanced
            if not think_content.startswith("<p>"):
                think_content = "<p>" + think_content
            if not think_content.endswith("</p>"):
                think_content += "</p>"

            # Wrap in <think> tags
            fixed_think_content = f"<think>{think_content}</think>"
            print("fixed_think_content:", fixed_think_content)

            # Combine with answer
            final_response = fixed_think_content + "\n" + answer_content
        else:
            final_response = response_str

        return final_response

    except Exception as e:
        return f"Error processing response: {str(e)}"

        
@app.route('/', methods=['GET'])
def home():
    # Render the initial page
    return render_template('index.html', selected_length='medium')
    return render_template('index.html', selected_length='medium')
    

@app.route('/submit', methods=['POST'])
def submit():
    # Handle form submission via AJAX
    data = request.json
    query = data['query']
    length = data['length']
    
    # Map length selection to token count
    token_mapping = {
        'vshort': 128,
        'short': 256,
        'medium': 512,
        'long': 1024
    }
    max_tokens = token_mapping.get(length, 512)
    
    strict_query = f"{query}. {max_tokens} words maximum."
    
    llama_response = get_response("llama-3.3-70b-versatile", strict_query, max_tokens)
    deepseek_response = get_response("deepseek-r1-distill-llama-70b", strict_query, max_tokens)
    deepseek_response = extract_and_fix_think_content(deepseek_response)
    
    return jsonify({
        'llama_response': llama_response,
        'deepseek_response': deepseek_response
    })

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)