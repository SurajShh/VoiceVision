from flask import Flask, request, jsonify
import yt_dlp
import whisper
import os
import torch
from flask_cors import CORS
import shutil
import sys
from transformers import pipeline, PegasusForConditionalGeneration, PegasusTokenizer
from existing_code import youtube_to_mp3, chunk_audio, speech_to_text

app = Flask(__name__)
CORS(app)

def summarize_youtube_video(youtube_url, outputs_dir):
    raw_audio_dir = f"{outputs_dir}/raw_audio/"
    chunks_dir = f"{outputs_dir}/chunks"
    transcripts_file = f"{outputs_dir}/transcripts.txt"
    summary_file = f"{outputs_dir}/summary.txt"
    segment_length = 10 * 60  # chunk to 10 minute segments

    if os.path.exists(outputs_dir):
        shutil.rmtree(outputs_dir)
        os.mkdir(outputs_dir)

    audio_filename = youtube_to_mp3(youtube_url, output_dir=raw_audio_dir)
    chunked_audio_files = chunk_audio(audio_filename, segment_length=segment_length, output_dir=chunks_dir)
    transcriptions = speech_to_text(chunked_audio_files, transcripts_file)

    model_name = "google/pegasus-large"
    pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)
    summarizer = pipeline("summarization", model=model_name, tokenizer=pegasus_tokenizer, framework="pt")
    summary = summarizer(transcriptions, min_length=80, max_length=250)

    another_model="facebook/bart-large-cnn"
    summarizer1 = pipeline("summarization", model=another_model)
    bart_summary = summarizer1(transcriptions, max_length=250, min_length=80, do_sample=False)

    return summary[0]['summary_text'], bart_summary[0]['summary_text']

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    youtube_url = data['url']
    summary = summarize_youtube_video(youtube_url, 'outputs')
    return jsonify({"summary": summary})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    output_dir = 'outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, file.filename)
    file.save(file_path)
    
    segment_length = 10 * 60  # chunk to 10 minute segments
    chunked_audio_files = chunk_audio(file_path, segment_length=segment_length, output_dir=output_dir)
    transcriptions = speech_to_text(chunked_audio_files)
    
    model_name = "google/pegasus-large"
    pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)
    summarizer = pipeline("summarization", model=model_name, tokenizer=pegasus_tokenizer, framework="pt")
    summary = summarizer(transcriptions, min_length=80, max_length=250)

    another_model="facebook/bart-large-cnn"
    summarizer1 = pipeline("summarization", model=another_model)
    bart_summary = summarizer1(transcriptions, max_length=250, min_length=80, do_sample=False)
    
    return jsonify({"summary": summary[0]['summary_text'], "bart_summary": bart_summary[0]['summary_text']})

if __name__ == '__main__':
    app.run(debug=True)
