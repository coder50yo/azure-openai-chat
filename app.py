import os
from flask import Flask, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from flask_talisman import Talisman

app = Flask(__name__)
csp = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline'",
    'style-src': "'self' 'unsafe-inline'",
    'img-src': "'self' data:",
    'connect-src': "'self'"
}
Talisman(app, content_security_policy=csp)
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
def apply_csp(response):
    csp_policy = (
        "default-src 'self'; "  # Allow content only from the same origin
        "script-src 'self'; "  # Allow scripts only from the same origin
        "style-src 'self' 'unsafe-inline'; "  # Allow inline styles (if necessary)
        "img-src 'self' data:; "  # Allow images from the same origin and data URIs
        "connect-src 'self'; "  # Allow API requests only to the same origin
    )
    response.headers["Content-Security-Policy"] = csp_policy
    return response

@app.route('/api/data', methods=['GET', 'POST'])
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
