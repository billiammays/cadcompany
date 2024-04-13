from openai import OpenAI
from divination import separate_prose_and_code
import speech_recognition as sr
import sys
import pyttsx3
import socket
import os
from dotenv import load_dotenv

load_dotenv()

# openai settings
key = os.getenv("OPENAI_API_KEY")
personality = 'p.txt'
with open(personality, "r") as file:
    mode = file.read()
messages  = [{"role": "system", "content": f"{mode}"}]

# instantiate client
client = OpenAI(api_key=key)

'''
# speech recognition set-up
r = sr.Recognizer()
mic = sr.Microphone(device_index=0)
r.dynamic_energy_threshold=False
r.energy_threshold = 100
'''

# pyttsx3 setup
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 for male, 1 for female


# initialise to asleep
wake_word = 'listen'
sleep_word = 'sleep'
exit_word = 'enough'
awake = False

# custom exit exception
class ProgramExit(Exception):
    pass

# instantiate socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 56789
serv = '127.0.0.1'
s.bind((serv, port))
print(f'[CADGPT-SERVER] Server socket successfully created at {serv} {port}')
# listen and connect to client
s.listen(1)
print('[CADGPT-SERVER] Server socket is listening...')
conn, addr = s.accept()
print(f'[CADGPT-SERVER] Got connection from {addr}')

# main while loop where the conversation occurs
while True:
    '''
    with mic as source:
        print("\nListening...")
        r.adjust_for_ambient_noise(source, duration = 0.2)
        audio = r.listen(source)
        
        try:
            # clownery to allow whisper to understand the AudioData
            with open('raw_audio_data.wav', 'wb') as f:
                f.write(audio.get_wav_data())
            audio_wav = open('raw_audio_data.wav', 'rb')
            # calling whisper
            user_input = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_wav, 
                response_format="text",
                language='en'
                )
    '''
    user_input = input('user input: ')
    try:
        # check for wake word
        if wake_word in user_input.lower():
            awake = True
        # check for sleep word
        elif sleep_word in user_input.lower():
            print('going to bed...')
            awake = False
        # shut down procedure
        elif exit_word in user_input.lower():
            raise ProgramExit()
    # shut down procedure raised
    except ProgramExit:
        print('shutting down...')
        sys.exit()
    # regular exception / nothing said
    except Exception as e:
        continue

    # if not awake, do not record audio and do not send to gpt
    if awake:
        # append to message bank
        messages.append({"role" : "user", "content" : user_input})
        # gpt calll
        completion = client.chat.completions.create(
            model='gpt-4-turbo',
            messages=messages
        ) 
        # choose and print response
        response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": response})
        print(f"\n{response}\n")
        # split prose and code
        prose, code = separate_prose_and_code(response)
        # send code to fusion
        conn.send(code.encode())
        # tts speak prose
        engine.say(f'{prose}')
        engine.runAndWait()