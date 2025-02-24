from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import openai
import requests
import os

# Set up Twilio and OpenAI credentials
TWILIO_ACCOUNT_SID = "AC534c37e22f24f57f9894623c052db70e"
TWILIO_AUTH_TOKEN = "4655276092d63f9973e0dec70bbf3a7b"
TWILIO_PHONE_NUMBER = "+17349925067"
OPENAI_API_KEY = "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"

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)

# Function to generate AI response using OpenAI
def generate_ai_response(user_input):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI sales representative. Your goal is to sell a course and book a Google Meet demo."},
            {"role": "user", "content": user_input},
        ]
    )
    return response["choices"][0]["message"]["content"]

# Convert AI response to speech using OpenAI TTS
def generate_speech(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.Audio.create(
        model="tts-1",
        input=text,
        voice="alloy"
    )
    return response["audio_url"]

# Handle incoming calls
@app.route("/voice", methods=["POST"])
def voice_response():
    response = VoiceResponse()
    response.say("Hello! This is your AI assistant. I am here to help you with our course offerings. How can I assist you?", voice="alice")

    # Record user speech and process in real-time
    response.record(timeout=5, transcribe=True, action="/process_audio")

    return str(response)

# Process user speech in real-time
@app.route("/process_audio", methods=["POST"])
def process_audio():
    user_speech = request.form.get("SpeechResult", "")
    print(f"User said: {user_speech}")

    ai_response = generate_ai_response(user_speech)
    speech_url = generate_speech(ai_response)

    response = VoiceResponse()
    response.play(speech_url)
    response.record(timeout=5, transcribe=True, action="/process_audio")

    return str(response)

# Initiate a Google Meet booking
@app.route("/book_meet", methods=["POST"])
def book_google_meet():
    user_email = request.json.get("email")

    if not user_email:
        return jsonify({"error": "Email required"}), 400

    meet_link = "https://meet.google.com/new"
    
    # Send a message with the meeting link
    message = client.messages.create(
        body=f"Your Google Meet demo is scheduled: {meet_link}",
        from_=TWILIO_PHONE_NUMBER,
        to=user_email
    )

    return jsonify({"message": "Google Meet scheduled", "meet_link": meet_link})

if __name__ == "__main__":
    app.run(debug=True)