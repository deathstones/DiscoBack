import json
import os
import shutil
from datetime import datetime

import requests

print(
    "[+] Want to backup your Discord account automatically every time you boot your computer? Look no further!\n"
    "[+] https://github.com/ExoticusFruit/DiscoBack/blob/main/README.md#running-this-script-on-startup"
)

running_directory = os.path.dirname(os.path.abspath(__file__))

with open(f"{running_directory}//config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
    token = config["discord_token"]
    backup_path = config["backup_path"]

og_backup_path = backup_path
backup_time = datetime.now().strftime("%d-%m-%y @ %H-%M")
backup_path = f"{backup_path}\\{backup_time}"
if not os.path.exists(backup_path):
    os.makedirs(backup_path)


class URLs:
    me = "https://discord.com/api/v9/users/@me"
    relationships = "https://discord.com/api/v9/users/@me/relationships"
    settings = "https://discord.com/api/v9/users/@me/settings"
    guilds = "https://discord.com/api/v9/users/@me/guilds"


headers = {
    "Accept": "*/*",
    "Cookie": "locale=en-GB",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/113.0.0.0 Safari/537.36",
    "Authorization": token,
}

# Backup basic account information & check if token is valid.
info_request = requests.get(URLs.me, headers=headers, timeout=10)
if info_request.status_code != 200:
    print("Invalid Discord token provided.")

info_json = info_request.json()
with open(f"{backup_path}\\self.txt", "w", encoding="utf-8") as file:
    file.write(
        f"Username: {info_json['username']}\nGlobal Name: {info_json['global_name']}\n"
        "Email: {info_json['email']}\nPhone: {info_json['phone']}\nBio:\n{info_json['bio']}"
    )
print("[+] Backed up basic info.")

if info_json["banner"] is not None:
    with open(f"{backup_path}\\banner.gif", "wb") as f:
        f.write(
            requests.get(
                f"https://cdn.discordapp.com/avatars/{info_json['id']}/{info_json['banner']}.gif?size=4096",
                timeout=10,
            ).content
        )
    print("[+] Backed up profile banner.")
if info_json["avatar"] is not None:
    with open(f"{backup_path}\\pfp.png", "wb") as f:
        f.write(
            requests.get(
                f"https://cdn.discordapp.com/avatars/{info_json['id']}/{info_json['avatar']}.png?size=1024",
                timeout=10,
            ).content
        )
    print("[+] Backed up profile picture.")

# Backup friends list.
friends_list = requests.get(URLs.relationships, headers=headers, timeout=10).json()
with open(f"{backup_path}\\friends.txt", "w", encoding="utf-8") as f:
    i = 0
    f.write("ID - Username - Display Name - Nickname\n")
    for entry in friends_list:
        i += 1
        user_info = entry["user"]
        if i is len(friends_list):
            f.write(
                f"{user_info['id']} - {user_info['username']} - {user_info['global_name']} - {entry['nickname']}"
            )
        else:
            f.write(
                f"{user_info['id']} - {user_info['username']} - {user_info['global_name']} - {entry['nickname']}\n"
            )
print(f"[+] Backed up {len(friends_list)} friends.")

# Backup joined guilds.
guild_list = requests.get(URLs.guilds, headers=headers, timeout=10).json()
with open(f"{backup_path}\\guilds.txt", "w", encoding="utf-8") as f:
    i = 0
    f.write("ID - Name - Owner\n")
    for entry in guild_list:
        i += 1
        if i is len(guild_list):
            f.write(f"{entry['id']} - {entry['name']} - {entry['owner']}")
        else:
            f.write(f"{entry['id']} - {entry['name']} - {entry['owner']}\n")
print(f"[+] Backed up {len(guild_list)} guilds.")

# Backup Discord settings.
with open(f"{backup_path}\\settings.txt", "w", encoding="utf-8") as f:
    f.write(requests.get(URLs.settings, headers=headers, timeout=10).text)
print("[+] Backed up Discord settings.")

# Write the metadata.
metadata = {
    "banner": f"{backup_path}\\banner.gif",
    "date": f"{backup_time}",
    "friends": f"{backup_path}\\friends.txt",
    "guilds": f"{backup_path}\\guilds.txt",
    "pfp": f"{backup_path}\\pfp.png",
    "self": f"{backup_path}\\self.txt",
    "settings": f"{backup_path}\\settings.txt",
}
if info_json["banner"] is None:
    metadata.pop("banner")
if info_json["avatar"] is None:
    metadata.pop("pfp")
with open(f"{backup_path}\\metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)
print("[+] Wrote metadata to metadata file.")

# Zipping the folder.
shutil.make_archive(
    f"{og_backup_path}/Discord Backup @ {backup_time}", "zip", backup_path
)
print(f"[+] Zipped up backup to Discord Backup @ {backup_time}.")

# Deleting the normal folder.
shutil.rmtree(backup_path)
print("[+] Deleted original backup folder.")
