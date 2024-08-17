import base64
import time
from PIL import Image
import io
from flask import *
import google.generativeai as genai
from config import *

if api_token == "YOUR_API_TOKEN":
    raise Exception("Replace `YOUR_API_TOKEN` with your Gemini API token in `config.py`")


app = Flask(__name__)
genai.configure(api_key=api_token)

generation_config = genai.GenerationConfig(
    temperature=0.3,
    response_mime_type="text/plain",
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    system_instruction="You are an assistant called Bowery. Answer in the language the user speaks."
)

chat_session = model.start_chat(
    history=[]
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    def stream():
        data = json.loads(request.data)
        img_data = base64.b64decode(data["image"])
        audio_data = data["audio"]
        image = Image.open(io.BytesIO(img_data))
        if audio_data == "Undefined":
            response = chat_session.send_message([data["message"], image], stream=True)
        else:
            response = chat_session.send_message([data["message"], image, {
                "mime_type": "audio/wav",
                "data": base64.b64decode(audio_data)
            }], stream=True)

        for chunk in response:
            yield json.dumps({"type": "answer", "text": chunk.text})
            yield "-|BOWERY SPLIT|-"

    return stream_with_context(stream())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True, ssl_context=('cert/server.crt', 'cert/server.key'))
