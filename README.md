# DiscordBot

This is a simple Discord bot written in Python using the nextcord library. It provides various commands including music playback, chat with GPT-3, and more.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/snowythevulpix/DiscordBot.git
   ```

2. Navigate to the project directory:

   ```bash
   cd DiscordBot
   ```

3. Install dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory and add your Discord bot token:

   ```
   token="your token"
   ```

   Replace `your token` with your actual Discord bot token.

## Usage

Once you've installed the dependencies and set up your `.env` file, you can run the `index.py` file to start the bot:

```bash
python index.py
```

## Commands

- `!ping`: Check the bot's latency.
- `!sum <num1> <num2>`: Add two numbers.
- `!div <num1> <num2>`: Divide two numbers.
- `!prod <num1> <num2>`: Multiply two numbers.
- `!hello`: Greet the user.
- `!info`: Display information about the server.
- `!p <search_query>`: Search and play a song from YouTube.
- `!join`: Join the voice channel of the user who issued the command.
- `!exit`: Disconnect from the voice channel.
- `!loop`: Toggle loop mode for the current song.
- `!pause`: Pause the currently playing music.
- `!resume`: Resume paused music playback.
- `!stop`: Stop music playback.
- `!volume <volume>`: Adjust the volume of the music.
- `!next`: Skip to the next track in the queue.
- `!coinflip`: Flip a coin.
- `!clear <amount>`: Clear a specified number of messages in the channel.
- `!view`: View the current music queue.

Feel free to modify and extend the functionality of the bot as needed. For more information, refer to the source code and the nextcord documentation.
