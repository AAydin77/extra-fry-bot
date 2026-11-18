import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
from dotenv import load_dotenv
import random
import json


load_dotenv()
PANEL_URL = os.getenv("PANEL_URL")
PANEL_KEY = os.getenv("PANEL_KEY")
SERVER_ID = os.getenv("SERVER_ID")
OWNER_ID = int(os.getenv("OWNER_ID"))
TRUSTED_ROLE_ID = {int(x) for x in os.environ["TRUSTED_ROLE_ID"].split(",")}
list_of_EITYSEF_members = json.loads(os.environ['list_of_EITYSEF_members'])
server_is_starting = {"is_starting": "False"}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("ERROR: missing argument for the command!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("ERROR: invalid data type for atleast one argument!")
    elif isinstance(error,commands.CommandNotFound):
        x = random.choice(list_of_EITYSEF_members)
        await ctx.send(f"Daym bruh: idrk what that command is, but yk who would?... *{x}*")
    else:
        raise error

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands")

#!prefixed commands
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


#Class views
#confirm start server class buttons thingy
class ConfirmView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.value = None
    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user_id
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(title="Confirmed", description="Sending the start signal...", color=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(title="Cancelled", description="Nothing was started.", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()


#slash tree commands


@bot.tree.command(name="say", description="I will say the sentence you give me!")
@app_commands.describe(user_msg="What do you want me to say?", mention="Who do you want to @?")
async def say(interaction: discord.Interaction, user_msg: str, mention: discord.Member = None):
    if mention != None:
        await interaction.response.send_message(f"{mention.mention}, {user_msg}")
        return
    await interaction.response.send_message(f"{user_msg}")

@bot.tree.command(name="wave", description="wave to someone!")
async def wave(interaction: discord.Interaction, mention: discord.Member = None):
    if mention:
        await interaction.response.send_message(mention.mention)
        await interaction.followup.send(f"https://klipy.com/gifs/greetings-PSr")
        return
    await interaction.response.send_message(f"https://klipy.com/gifs/greetings-PSr")





#MINECRAFT RELATED DISCORD BOT COMMANDS
#Status of minecraft server command

@bot.tree.command(name="status_of_mc_server", description="Get the status of the minecraft server")
async def get_status(interaction: discord.Interaction):
    url = f"{PANEL_URL}/api/client/servers/{SERVER_ID}/resources"
    headers = {
        "Authorization": f"Bearer {PANEL_KEY}",
        "Accept": "application/json",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 401:
                    await interaction.response.send_message("The bot's panel key isn't working.", ephemeral=True)
                    print("The bot's panel key isn't working.")
                    return
                if response.status == 404:
                    await interaction.response.send_message("I can't find that server on the panel.", ephemeral=True)
                    print("I can't find that server on the panel.")
                    return
                if response.status != 200:
                    await interaction.response.send_message(f"The panel gave an unexpected answer ({response.status}).", ephemeral=True)
                    print(f"The panel gave an unexpected answer ({response.status}).")
                    return
                data = await response.json()
                state = (data["attributes"]["current_state"])
                
    except(aiohttp.ClientError, asyncio.TimeoutError):
        await interaction.response.send_message("I can't reach the panel right now.", ephemeral=True)
        print("I cant see the panel right now. (hint: check the .env's panel settings, or if the panel is powered on.)")
        return


    embed = discord.Embed(title="MC server status")
    if state == "running":
        embed.add_field(name="Status", value=f"The server is: {state}. ✅",)
        embed.color= discord.Color.green()
    else:
        embed.add_field(name="Status", value=f"The server is: {state}. 🛑" )
        embed.color= discord.Color.red()
    
    await interaction.response.send_message(embed=embed)
            


#HELPER FUNCTION TO CHECK IF SERVER IS RUNNING WITH BEAUTIFUL EMBEDS

async def watch_until_running(interaction, base, headers):
    try:
        for x in range(20):
            timeout = aiohttp.ClientTimeout(total=2)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{base}/resources", headers=headers) as response: 
                    if response.status != 200:
                        print (f"The panel gave an unexpected answer ({response.status}).")
                    data = await response.json()
                    state = data["attributes"]["current_state"]
                    
            #Check if server is offline
            if state == "running":
                embed = discord.Embed(title="Server is running!", description="Have fun!", colour=discord.Colour.green())
                await interaction.edit_original_response(embed=embed)
                await interaction.followup.send(f"{interaction.user.mention} the server is up!", ephemeral=True)
                return True
            
            await asyncio.sleep(3)
            embed = discord.Embed(title="Starting server...", description="Status: starting.", color=discord.Color.orange())
            embed.set_footer(text=f"checking status... {x}")
            await interaction.edit_original_response(embed=embed)
            
        embed = discord.Embed(title="ERROR: Something took too long to respond", description=f"Sorryyy, maybe try again a little later? \n \n (Current server state: {state}) \n (Hint: maybe there is an error with the panel causing it to never start up properly)")
        await interaction.edit_original_response(embed=embed)
        return True

    except(aiohttp.ClientError, asyncio.TimeoutError):
        print ("ERROR: I can't reach the panel right now. (Hint: make sure the panel is powered on. Maybe the timout is too short?)")
        
        embed = discord.Embed(title="ERROR: I can't reach the panel!", description="My arms are so short I can't reach the panel bruhhhh. (Hint: ClientError/TimeoutError. If Aydin wasn't lazy he would've made a logging system to tell you why this error occured.)")
        embed.set_footer(text="Is the panel powered on? Is it pointed to the correct panel url? Maybe timeout is too short?")
        await interaction.edit_original_response(embed=embed)



#HELPER FUNCTION TO START THE SERVER IF IT IS OFFLINE.
async def start_server_if_offline(base, headers):
    try:
        timeout = aiohttp.ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{base}/resources", headers=headers) as response: 
                if response.status != 200:
                    return False, f"The panel gave an unexpected answer ({response.status})." 
                data = await response.json()
                
            #Check if server is offline
            state = data["attributes"]["current_state"]
            if state != "offline":
                return False, f"The server can't be started. (current state: {state})"
            
            #Make sure that the User is trusted with the other method, then send POST request to power on the server
            async with session.post(f"{base}/power", headers=headers, json={"signal": "start"}) as response:
                if response.status != 204:
                    return False, f"The panel refused to power up. ({response.status})"
                return True, "Signal sent successfully!"
    except(aiohttp.ClientError, asyncio.TimeoutError):
        return False, "ERROR: I can't reach the panel right now. (Hint: make sure the panel is powered on. Maybe the timout is too short?)"


#Helper for checking if the state is running

async def is_state_running(base, headers):
    timeout = aiohttp.ClientTimeout(total=2)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f"{base}/resources", headers=headers) as response: 
            if response.status != 200:
                state = "ERROR"
                return state, (f"The panel gave an unexpected answer ({response.status}).")
            data = await response.json()
            state = data["attributes"]["current_state"]
            return state, (f"response status: ({response.status}).")


#start mc server command
@bot.tree.command(name="start_mc_server", description="Start the Minecraft server!")
@app_commands.guild_only()
async def startserver(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member):
        return
    is_owner = interaction.user.id == OWNER_ID
    has_role = any(role.id in TRUSTED_ROLE_ID for role in interaction.user.roles)
    if not (is_owner or has_role):
        await interaction.response.send_message("You do not have the required role to perform this command. Hint: Ask Aydin to give you the role or something idk, maybe he hates you hahaaha.", ephemeral=True)
        return
    
    headers = {
        "Authorization": f"Bearer {PANEL_KEY}",
        "Accept": "application/json",
    }
    base = f"{PANEL_URL}/api/client/servers/{SERVER_ID}"
    state, message = await is_state_running(base,headers)
    
#confirm to send power request to start the server embed screen
    embed = discord.Embed(title="Start the Minecraft server?", 
                          description="⚡️ send a signal to power on the server?", 
                          color=discord.Color.blurple()
                        )
    embed.set_footer(text="This prompt will expire in 30 seconds.")
    
#make user to confirm yes or cancel
    view = ConfirmView(interaction.user.id)
    await interaction.response.send_message("", embed=embed, view=view, ephemeral=True)
    await view.wait()
    if view.value is None:
        await interaction.edit_original_response(content="Timed out, nothing was started.", view=None)
        embed = discord.Embed(title="Timed out.", colour=discord.Color.darker_grey())
        return
    if not view.value:
        return
    
    if state == "running" or server_is_starting["is_starting"] == "True":
        embed = discord.Embed(title="Server is already running, or is starting up.", colour=discord.Color.brand_green())
        if state == "starting" or server_is_starting["is_starting"] == "True":
            embed.set_footer(text="Current server status: starting...")
            await interaction.edit_original_response(embed=embed,)
        else:
            embed.set_footer(text="Current server status: Running")
            await interaction.edit_original_response(embed=embed,)
        print(f"I won't send a power signal because: \nserver state: {state} \nmy variable state: {server_is_starting['is_starting']}")
        return
    print (f"I will send a power signal because: \nserver state: {state} \nmy variable state: {server_is_starting['is_starting']}")
    
    
#sending post request via the helper function
    signal_sent, message = await start_server_if_offline(base, headers)
    if signal_sent:
        server_is_starting["is_starting"] = "True"
        embed = discord.Embed(title="Starting server...", description="Status: starting.\n pls wait... <3", color=discord.Color.orange())
        await interaction.edit_original_response(embed=embed,)


#loop a status check and wait until the server is up to ping the user via the watch_until_running() helper

    started = await watch_until_running(interaction, base, headers)
    if started == True:
        server_is_starting["is_starting"] = "False"



bot.run(os.environ["TOKEN"])


