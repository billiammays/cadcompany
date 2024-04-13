import pyaudio
import wave

import openai

import re

# Function to record audio from microphone (pyaudio)
def record_audio(file_path, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* Recording audio...")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Finished recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# audio transcription
def whisper(audio):
    with open('speech.wav','wb') as f:
        f.write(audio.get_wav_data())
    speech = open('speech.wav', 'rb')
    wcompletion = openai.Audio.transcribe(
        model = "whisper-1",
        file=speech
    )
    user_input = wcompletion['text']
    print(user_input)
    return user_input

# separate ChatGPT replies into prose and code
def separate_prose_and_code(input_string):
    # monkeyest method of doing so
    prose = ''
    code = ''
    input_ls = input_string.split("```")
    for i in range(len(input_ls)):
        if i % 2 == 0:
            prose += input_ls[i]
        else:
            trimmed = input_ls[i][6::]
            code += trimmed
    if code == '':
        code = 'no code sent'
    return prose, code