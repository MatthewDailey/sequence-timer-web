import os
import json
import argparse
from elevenlabs import set_api_key, generate

set_api_key(os.environ["ELEVEN_LABS_API_KEY"])


def tts_elevenlabs(text, save_to_path):
    audio = generate(
        text=text,
        voice="XB0fDUnXU5powFXDhCwa",  # Charlette
        model="eleven_monolingual_v1",
    )
    with open(save_to_path, "wb") as binary_file:
        binary_file.write(audio)


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
