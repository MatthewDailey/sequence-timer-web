import os
import json
import argparse
from elevenlabs.client import ElevenLabs

# Premade voice for API (Voice Library voices like Charlette are blocked on free tier; override with ELEVEN_LABS_VOICE_ID).
DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
DEFAULT_MODEL_ID = "eleven_flash_v2_5"


def _api_key() -> str:
    key = os.environ.get("ELEVEN_LABS_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError(
            "Set ELEVEN_LABS_API_KEY or ELEVENLABS_API_KEY to your ElevenLabs API key."
        )
    return key


def tts_elevenlabs(text, save_to_path):
    voice_id = os.environ.get("ELEVEN_LABS_VOICE_ID", DEFAULT_VOICE_ID)
    model_id = os.environ.get("ELEVEN_LABS_MODEL_ID", DEFAULT_MODEL_ID)
    client = ElevenLabs(api_key=_api_key())
    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        output_format="mp3_22050_32",
    )
    with open(save_to_path, "wb") as binary_file:
        for chunk in audio_stream:
            if chunk:
                binary_file.write(chunk)


AUDIO_URL = "audio_url"
OUTPUT_DIRECTORY = "public/audio"


def main(args):

    with open(args.sequence_file) as f:
        sequence = json.load(f)
        print("Generating audio for sequence: ", sequence["name"])
        for item in sequence["sequence"]:
            text = item["name"] + ". " + str(item["duration"]) + " seconds"
            id = item["name"].lower().replace(" ", "-") + "-" + str(item["duration"])
            if AUDIO_URL in item:
                print("Found audio_url in item: ", item[AUDIO_URL])
                audio_path = "public" + item[AUDIO_URL]
            else:
                audio_path = os.path.join(OUTPUT_DIRECTORY, id + ".mp3")
            if os.path.exists(audio_path):
                print("Found audio at path: ", audio_path)
            else:
                tts_elevenlabs(text, audio_path)
                print(f"Generated audio for {text} at path: {audio_path}")
            item[AUDIO_URL] = audio_path.replace("public/", "/")
        print("Saving sequence with audio to: ", args.sequence_file)
        with open(args.sequence_file, "w") as f:
            json.dump(sequence, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate audio for sequence.")
    parser.add_argument(
        "-s",
        "--sequence-file",
        type=str,
        required=True,
        help="Sequence json file that needs audio.",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        type=str,
        default="public/audio",
        help="Path to save audio to.",
    )
    main(parser.parse_args())
