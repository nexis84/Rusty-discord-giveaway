# Discord Giveaway Bot

A simple Discord bot that allows you to run giveaways in your server.

## Features

- Start a giveaway with a prize and duration
- Users enter by reacting with 🎉
- Automatically picks a winner when time expires
- Announces the winner in the channel

## Setup

1. Create a Discord bot at https://discord.com/developers/applications
2. Copy the bot token
3. Set the `DISCORD_TOKEN` environment variable to your bot token
4. Invite the bot to your server with appropriate permissions (Send Messages, Use Slash Commands, Read Message History, Add Reactions)

## Local Installation

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variable: `export DISCORD_TOKEN=your_token_here` (or use .env file)
4. Run the bot: `python bot.py`

## Deployment on Render

1. Push this code to a GitHub repository
2. Connect your GitHub repo to Render (render.com)
3. Create a new Web Service from the repo
4. Render will auto-detect the Python app and use `render.yaml`
5. Set the `DISCORD_TOKEN` environment variable in Render's dashboard
6. Deploy!

## Usage

Use the `/giveaway` slash command:

- `prize`: The prize description
- `duration`: Duration in minutes

Example: `/giveaway prize: A free game duration: 60`

Users react with 🎉 to enter. When time is up, a winner is randomly selected and announced.

## Usage

Use the `/giveaway` slash command:

- `prize`: The prize description
- `duration`: Duration in minutes

Example: `/giveaway prize: A free game duration: 60`

Users react with 🎉 to enter. When time is up, a winner is randomly selected and announced.