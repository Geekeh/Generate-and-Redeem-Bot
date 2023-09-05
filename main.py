# github/cxstles
# Sep 5th, 2023.
# ily :)

from discord.ext import commands
from os import environ as env
import discord
import uuid
import json
import os


_config = open("./data/config.json")
_config = json.load(_config)
_bot = commands.Bot(
  command_prefix=".", 
  intents=discord.Intents.all(), 
  help_command=None
)


class KeySystem:
    def __init__(self, limit: int = 30):
        self.limit = 30
        self.keys = {}

    def all_keys(self):
        return self.keys

    def add_keys(self, uid: int, num: int = 3):
        for _ in range(num):
            self.keys[uid].append({"key": str(uuid.uuid4())})
            self.save_keys(uid)
        return f"added {num} keys."

    def intitate_sys(self, uid: int):
        if uid not in self.keys:
            self.keys[uid] = []
            self.load_keys(uid)

    def get_keys(self, uid: int):
        if uid in self.keys:
            self.load_keys(uid)
            return self.keys[uid][-self.limit :]
        return []

    def save_keys(self, uid):
        if uid in self.keys:
            keys = self.keys[uid]
            file_path = f"./data/{uid}.json"
            with open(file_path, "w") as file:
                json.dump(keys, file)

    def load_keys(self, uid):
        file_path = f"./data/{uid}.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    keys = json.load(file)
                    self.keys[uid] = keys
            except FileNotFoundError:
                pass
        else:
            self.save_keys(uid)


sys = KeySystem(_config["limit"])


@_bot.event
async def on_ready():
    print(f"Logged in as: {_bot.user}")
    await _bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
          type=discord.ActivityType.watching, 
          name="github/cxstles"
        ),
    )


@_bot.command()
async def gen(ctx, num: int = 3):
    if ctx.guild.id not in sys.all_keys():
        sys.intitate_sys(ctx.guild.id)

    if num <= 0:
        await ctx.reply(f"{num} is invalid, please choose a valid amount.")
    sys.add_keys(ctx.guild.id, num)
    await ctx.reply(f"added {num} keys, please do `.keys` to view all of them.  ")


@_bot.command()
async def keys(ctx):
    msg = ""
    if ctx.author.id != _config["owner"]:
        await ctx.reply("Sorry, you don't have the permissions to view all keys.")

    sys.load_keys(ctx.guild.id)
    for i in sys.get_keys(ctx.guild.id):
        msg += f"{i['key']}\n"
    await ctx.reply(f"List of Keys: \n\n``{msg}``")


@_bot.command()
async def redeem(ctx, key: str = ""):
    sys.load_keys(ctx.guild.id)
    if len(key) != 36:
        await ctx.reply(f"``{key}`` is invalid, please try again.")

    for i in range(len(sys.all_keys()[ctx.guild.id])):
        if sys.get_keys(ctx.guild.id)[i]["key"] == key:
            sys.all_keys()[ctx.guild.id].pop(i)
            sys.save_keys(ctx.guild.id)
            role = discord.utils.get(
              ctx.guild.roles, 
              name=_config["role"]
            )
            await ctx.author.add_roles(role)
            await ctx.reply(f"Redeemed {key}.")
    await ctx.reply(f"``{key}`` is invalid, please try again.")

_bot.run(env["token"], reconnect=True)

