# The Extra Fry Discord Bot

Start your Pelican panel MC servers via a Discord bot! + some other things...

This is just a little Discord bot that I made to exercise and strengthen my VERY amateur coding skills. I wanted to explore and learn about calling APIs and using Discord's bot integration with discord.py. The main purpose of this Discord bot is to give my friends a way to start my Minecraft server, which I am hosting locally via Pelican. This bot also has some personalized commands and error messages mainly for me and my friends, so this bot probably shouldn't be taken as super serious. I just wanted to give programming a go, along with uploading this to GitHub because I have never done it before but always wanted to!

Ok, love you see ya, bye :).

---

## Commands

- `/start_mc_server` - starts the Minecraft server
- `/status_of_mc_server` - shows whether the server is online
- `/wave` - sends a wave gif in the chat
- `/say` - sends what you will it to say.
- `!ping` - replies back "Pong!"

## Quick setup

1. Clone the repo and open the folder:
   ```
   git clone https://github.com/AAydin77/extra-fry-bot.git
   cd extra-fry-bot
   ```
2. Create a venv and install the packages in `requirements.txt`. Make sure all of them are installed, as the script will not work otherwise:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Fill in the `.env` (see Configuration below), then run the bot:
   ```
   python main.py
   ```

## Configuration

1. Create a Discord bot via the developer portal, ensuring that you allow message intents.
2. Paste the bot's token into the example .env and rename it to `.env`.
3. Create an empty test Discord server to invite the bot to.
4. Once invited, add your owner ID into the `.env`.
5. Create a role for users to be assigned so that they have permission to start the MC server.
6. Make a list of your friends' names and put them into the `list_of_EITYSEF_members` variable I guess??
7. Add the URL the Pelican panel is accessible from (this URL must be accessible from the device running this script).
8. Create a client token from the profile menu and copy the **full** token from the popup notification at the top right of your screen. Then paste that into the `.env` under `PANEL_KEY`.
9. Go to the Minecraft server you wish to be remotely startable by the bot and find the shortened server ID. Paste that into `SERVER_ID` in the `.env`. (As of right now you can only add one server to be started up, and I plan to update it to support multiple servers in the future.)

After saving and inputting all of those into the `.env`, you hypothetically should be able to start the bot with no issues?!?!!? Test it by running the script and then checking if the bot is online in Discord. Try using `/start_mc_server` and check your Pelican panel to see the status of your mc server and whether it is actually starting up.
