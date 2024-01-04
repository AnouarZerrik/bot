import telebot
from telebot import types
from PIL import Image
import google.generativeai as genai
import os

import requests

import whisper
model_wis = whisper.load_model('base')

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/7bc7c4277390e0272777422931809d71/ai/run/"
headers = {"Authorization": "Bearer OI2zOAR2bfUbkjkKxqVExdHzzeMjtw75Pyym62RE"}

def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


genai.configure(api_key='AIzaSyBLdPt9xCo9Ia1vpBuxfCl9EMq0FqXByyI')
model = genai.GenerativeModel('gemini-pro-vision')

# Replace 'YOUR_BOT_TOKEN' with the actual token you get from BotFather on Telegram
bot = telebot.TeleBot('6422562378:AAHgHSh8ef1UiqeCnL_JYXC--3Mr0n_aRtI')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! I am your bot.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Get the file_id of the largest photo in the list
    file_id = message.photo[-1].file_id

    # Get file information
    file_info = bot.get_file(file_id)

    # Download the photo
    downloaded_file = bot.download_file(file_info.file_path)

    #image = Image.open(downloaded_file)

    #response = model.generate_content(['Give me descrption of this image',image])

    # Save the photo locally (you can customize the file name)
    with open(f"/media/{file_id}.png", 'wb') as new_file:
       new_file.write(downloaded_file)

    image = Image.open(f"/media/{file_id}.png")

    if message.caption is not None:
        try :
          response = model.generate_content([message.caption,image] , stream=False)
          response.resolve()
          bot.reply_to(message, response.text )
        except :
          bot.reply_to(message, 'Do that again!! ' )
    else :
      bot.reply_to(message, 'Add the caption of this image' )

    os.remove(f"/media/{file_id}.png")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    inputs = [
    { "role": "system", "content": "your are freindly bot telegrame assistance, your name is ANZER-GPT powered by Anoir Zerrik " },
    { "role": "user", "content":  message.text}]
    output = run("@cf/meta/llama-2-7b-chat-int8", inputs)
    bot.reply_to(message, output['result']['response'])



@bot.message_handler(content_types=['audio', 'voice'])
def handle_audio(message):
    # Get the file_id of the audio
    file_id = message.audio.file_id if message.content_type == 'audio' else message.voice.file_id

    # Get file information
    file_info = bot.get_file(file_id)

    # Download the audio
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the audio locally (you can customize the file name and extension)
    with open(f"/media/{file_id}.ogg", 'wb') as new_file:
        new_file.write(downloaded_file)


    result = model_wis.transcribe(f"/media/{file_id}.ogg" , fp16=False)
    #print(result['text'])

    inputs = [
    { "role": "system", "content": "your are freindly bot telegrame assistance, your name is ANZER-GPT powered by Anoir Zerrik " },
    { "role": "user", "content":  result['text']}]


    
    output = run("@cf/meta/llama-2-7b-chat-int8", inputs )
    try :
      bot.reply_to(message, output['result']['response'])
    except:
      bot.reply_to(message, result['text'])

    os.remove(f"/media/{file_id}.ogg")


if __name__ == "__main__":
    bot.polling(none_stop=True)
