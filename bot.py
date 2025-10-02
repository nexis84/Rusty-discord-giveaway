import discord
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta
import os
from flask import Flask
import threading

TOKEN = os.getenv('DISCORD_TOKEN')

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
    await tree.sync()
    print(f'Logged in as {bot.user}')

def run_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)