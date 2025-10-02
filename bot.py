import discord
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
import os
from flask import Flask
import threading

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')  # optional: when set, commands will sync to this guild for instant testing
SYNC_COMMANDS = os.getenv('SYNC_COMMANDS', 'true').lower() == 'true'  # set to 'false' to disable command registration from this instance

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

giveaways = {}  # channel_id: {"message_id": id, "end_time": datetime, "prize": str, "participants": set}

@tree.command(name="giveaway", description="Start a giveaway with a prize and duration in minutes")
async def giveaway_command(interaction: discord.Interaction, prize: str, duration: int):
    if interaction.channel_id in giveaways:
        await interaction.response.send_message("A giveaway is already running in this channel!", ephemeral=True)
        return

    end_time = datetime.now() + timedelta(minutes=duration)
    embed = discord.Embed(
        title="🎉 Giveaway! 🎉",
        description=f"**Prize:** {prize}\n**Ends at:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}\nReact with 🎉 to enter!",
        color=0x00ff00
    )
    embed.set_footer(text="Good luck!")

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()

    await message.add_reaction("🎉")

    giveaways[interaction.channel_id] = {
        "message_id": message.id,
        "end_time": end_time,
        "prize": prize,
        "participants": set()
    }

    await asyncio.sleep(duration * 60)

    if interaction.channel_id in giveaways:
        giveaway = giveaways[interaction.channel_id]
        participants = giveaway["participants"]
        if participants:
            winner = random.choice(list(participants))
            embed = discord.Embed(
                title="🎉 Giveaway Ended! 🎉",
                description=f"**Prize:** {giveaway['prize']}\n**Winner:** {winner.mention}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("No one entered the giveaway. Better luck next time!")
        del giveaways[interaction.channel_id]

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if reaction.emoji == "🎉":
        channel_id = reaction.message.channel.id
        if channel_id in giveaways:
            giveaway = giveaways[channel_id]
            if giveaway["message_id"] == reaction.message.id:
                giveaway["participants"].add(user)

@bot.event
async def on_ready():
    # Sync commands. If GUILD_ID is set, sync to that guild for instant availability (useful for testing).
    try:
        if not SYNC_COMMANDS:
            print("Command sync disabled by SYNC_COMMANDS env var")
        else:
            if GUILD_ID:
                try:
                    guild_obj = discord.Object(id=int(GUILD_ID))
                    synced = await tree.sync(guild=guild_obj)
                    print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
                except Exception as e:
                    print(f"Failed to sync to guild {GUILD_ID}: {e}")
                    # fallback to global sync
                    synced = await tree.sync()
                    print(f"Synced {len(synced)} global commands (fallback)")
            else:
                synced = await tree.sync()
                print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print("Command sync failed:", e)

    print(f'Logged in as {bot.user}')


def run_bot():
    bot.run(TOKEN)


if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)