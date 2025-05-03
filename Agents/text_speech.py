from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os
load_dotenv()

client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)
def speech(script, filename="voiceovers/output.mp3"):
    audio = client.text_to_speech.convert(
        text=script,
        voice_id="XrExE9yKIg1WjnnlVkGX",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    # Save the audio to a file
    with open(filename, "wb") as f:
        for chunk in audio:  # Iterate over the generator
            f.write(chunk)

    return f"Audio saved as {filename}"


