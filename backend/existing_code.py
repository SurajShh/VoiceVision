import os
import shutil
import librosa
import subprocess
from yt_dlp.utils import DownloadError
import yt_dlp
import soundfile as sf
from transformers import pipeline
import whisper
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

def find_audio_files(path, extension=".mp3"):
    """Recursively find all files with extension in path."""
    audio_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                audio_files.append(os.path.join(root, f))

    return audio_files

def youtube_to_mp3(youtube_url: str, output_dir: str) -> str:
    """Download the audio from a youtube video, save it to output_dir as an .mp3 file.

    Returns the filename of the saved video.
    """
    ydl_config = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "verbose": True,
    }

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Downloading video from {youtube_url}")

    try:
        with yt_dlp.YoutubeDL(ydl_config) as ydl:
            ydl.download([youtube_url])
    except DownloadError:
        # weird bug where youtube-dl fails on the first download, but then works on second try... hacky ugly way around it.
        with yt_dlp.YoutubeDL(ydl_config) as ydl:
            ydl.download([youtube_url])

    audio_filename = find_audio_files(output_dir)[0]
    return audio_filename


def chunk_audio(filename, segment_length, output_dir):
    """Chunk the audio file into segments of specified length (in seconds)."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load audio file
    audio, sr = librosa.load(filename, sr=None)

    # Calculate duration in seconds
    duration = librosa.get_duration(y=audio, sr=sr)

    # Calculate number of segments
    num_segments = int(duration / segment_length) + 1

    # Iterate through segments and save them
    for i in range(num_segments):
        start = i * segment_length * sr
        end = min((i + 1) * segment_length * sr, len(audio))
        segment = audio[start:end]
        sf.write(os.path.join(output_dir, f"segment_{i}.mp3"), segment, sr)

    # Find and return chunked audio files
    chunked_audio_files = find_audio_files(output_dir)
    return sorted(chunked_audio_files)


def speech_to_text(audio_files: list, output_file=None) -> list:
    print("Converting audio to text...")

    transcripts = []
    for audio_file in audio_files:
        model = whisper.load_model("base")  # Load Whisper model
        result = model.transcribe(audio_file)
        transcript = result["text"]
        transcripts.append(transcript)

    if output_file is not None:
        with open(output_file, "w") as file:
            pass  # Empty the file
        
        # Append all transcripts to the output file
        with open(output_file, "a") as file:
            for transcript in transcripts:
                file.write(transcript + "\n")

    print("Audio to text process Completed...")
    print(transcripts)
    return transcripts
