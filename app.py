import os
from flask import Flask, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
load_dotenv(override=True)

# Ensure environment variables are set
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Initialize the client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "script-src 'self' https://azure-openai-chat-eyb9fugmhahehmcp.canadacentral-01.azurewebsites.net;"
    return response

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_query = request.json.get("query")
    elif request.method == 'GET':
        user_query = request.args.get("query")

    try:
        # Create a chat completion
        response = client.chat.completions.create(
            model=deployment_name,  # Use the actual deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_query}
            ],
            max_tokens=800,
            temperature=0.7,
            stream=False,
        )
        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
