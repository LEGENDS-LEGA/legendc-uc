
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
import re
import os

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
collection = db['users']

api_id = '24235841'
api_hash = '5dcca0184e08a824d00aa0cc24c0a18c'
bot_token = '265477132:AAEcXjPC-RaFQWOaIS5Nys2CcKAwwl10pl8'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

@app.on_message(filters.command("adduser") & filters.private)
async def add_user(client, message: Message):
    if len(message.command) < 6:
        await message.reply("Usage: /adduser <phone_number> <first_name> <last_name> <email> <profile_picture_url> <additional_info>")
        return

    phone_number = message.command[1].strip()
    first_name = message.command[2].strip()
    last_name = message.command[3].strip()
    email = message.command[4].strip()
    profile_picture_url = message.command[5].strip()
    additional_info = " ".join(message.command[6:]).strip()

    user_data = {
        "phone_number": phone_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "profile_picture_url": profile_picture_url, 
        "additional_info": additional_info
    }

    collection.insert_one(user_data)
    await message.reply("User added successfully!")

@app.on_message(filters.photo | filters.animation & filters.private)
async def handle_media(client, message: Message):
    file = message.photo if message.photo else message.animation
    file_id = file.file_id
    file_extension = "gif" if message.animation else "jpg"
    file_path = f'downloads/{file_id}.{file_extension}'

    await message.download(file_path)

    await message.reply("Նկարը կամ GIF-ը պահպանված է:", reply_to_message_id=message.message_id)
    await message.reply_document(file_path) 

    await message.reply("Նշեք տվյալները հետևյալ տեսքով՝\n<phone_number> <first_name> <last_name> <email> <additional_info>:")

    @app.on_message(filters.text & filters.private)
    async def add_user_from_text(client, message: Message):
        text = message.text.strip().split()

        if len(text) < 5:
            await message.reply("Usage: <phone_number> <first_name> <last_name> <email> <additional_info>")
            return

        phone_number = text[0].strip()
        first_name = text[1].strip()
        last_name = text[2].strip()
        email = text[3].strip()
        additional_info = " ".join(text[4:]).strip()

        user_data = {
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "profile_picture_url": file_path, 
            "additional_info": additional_info
        }

        collection.insert_one(user_data)
        await message.reply("User added successfully!")

@app.on_message(filters.command("getuser") & filters.private)
async def get_user(client, message: Message):
    if len(message.command) != 2:
        await message.reply("Usage: /getuser <search_query>")
        return

    search_query = message.command[1].strip()
    query = {}

    if re.match(r"^\+\d+$", search_query): 
        query["phone_number"] = search_query
    elif re.match(r"^[A-Za-z]+$", search_query):  
        query["$or"] = [
            {"first_name": search_query},
            {"last_name": search_query}
        ]
    elif re.match(r"^[\w\.-]+@[\w\.-]+$", search_query):  
        query["email"] = search_query
    elif re.match(r"^http[s]?://", search_query): 
        query["profile_picture_url"] = search_query
    else:  
        query["additional_info"] = search_query

    user = collection.find_one(query)

    if user:
        response = (
            f"Phone Number: {user.get('phone_number', 'N/A')}\n"
            f"First Name: {user.get('first_name', 'N/A')}\n"
            f"Last Name: {user.get('last_name', 'N/A')}\n"
            f"Email: {user.get('email', 'N/A')}\n"
            f"Profile Picture URL: {user.get('profile_picture_url', 'N/A')}\n"
            f"Additional Info: {user.get('additional_info', 'N/A')}"
        )
        await message.reply(response)
    else:
        await message.reply("User not found!")

app.run()
