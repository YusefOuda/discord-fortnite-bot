import discord
import asyncio
import requests
import aiohttp
from datetime import datetime
import pdb
from keys import TRN_API_KEY, DISCORD_TOKEN
from ratelimit import rate_limited

client = discord.Client()


@asyncio.coroutine
@rate_limited(1)
def get_stats_embed(username, platform):
	resp = yield from get_stats_resp(username, platform)
	if resp.status != 200:
		embed = discord.Embed(
			title="Could not get stats for player " + username, colour=discord.Colour(0xe74c3c))
		return embed
	stats = yield from resp.json()
	if stats.get("error") and stats.get("message"):
		embed = discord.Embed(
			title=stats["message"], colour=discord.Colour(0xe74c3c))
		return embed
	if stats.get("error"):
		embed = discord.Embed(
			title=stats["error"], colour=discord.Colour(0xe74c3c))
		return embed
	return get_embed_message(stats, username, platform)


def get_embed_message(stats, username, platform):
	has_stats = False
	embed = discord.Embed(title="Full Stats", colour=discord.Colour(
		0x316a7b), url="https://fortnitetracker.com/profile/" + platform + "/" + username)
	embed.set_author(name=stats["epicUserHandle"] + " - " + stats["platformNameLong"],
					 url="https://fortnitetracker.com/profile/" + platform + "/" + username)
	has_stats = embed_stats_details(stats, embed)

	if has_stats == False:
		embed = discord.Embed(title="Could not get stats for player: " +
							  username + ", platform: " + platform, colour=discord.Colour(0xe74c3c))
		return embed
	return embed


@asyncio.coroutine
def get_stats_resp(username, platform):
	headers = {"TRN-Api-Key": TRN_API_KEY}
	r = yield from aiohttp.get("https://api.fortnitetracker.com/v1/profile/" + platform + "/" + username, headers=headers)
	return r


def embed_stats_details(stats, embed):
	title = "__Lifetime Stats__"
	rounds_played = get_stat(stats["lifeTimeStats"], "Matches Played")
	wins = get_stat(stats["lifeTimeStats"], "Wins")
	score = get_stat(stats["lifeTimeStats"], "Score")
	winpct = get_stat(stats["lifeTimeStats"], "Win%")
	kills = get_stat(stats["lifeTimeStats"], "Kills")
	kd = get_stat(stats["lifeTimeStats"], "K/d")
	time = get_stat(stats["lifeTimeStats"], "Time Played")
	survival_time = get_stat(stats["lifeTimeStats"], "Avg Survival Time")

	col1_text = "**Score**: " + score + "\n"
	col1_text += "**Matches Played**: " + rounds_played + "\n"
	col1_text += "**Wins**: " + wins + "\n"
	col1_text += "**Win%**: " + winpct
	col2_text = "**Kills**: " + kills + "\n"
	col2_text += "**K/d**: " + kd + "\n"
	col2_text += "**Avg Survival Time**: " + survival_time + "\n"
	col2_text += "**Time Played**: " + time
	embed.add_field(name=":trophy:", value=col1_text, inline=True)
	embed.add_field(name=":gun:", value=col2_text, inline=True)
	return True

def get_stat(stats, field):
	for stat in stats:
		if stat["key"] == field:
			return stat["value"]

@client.event
@asyncio.coroutine
def on_ready():
	print("Logged in as")
	print(client.user.name)
	print(client.user.id)
	print("------")
	yield from client.change_presence(game=discord.Game(name='.fortnitehelp'))

@client.event
@asyncio.coroutine
def on_message(message):
	if message.content.lower().startswith(".fortnitehelp"):
		help_message = "To check stats, type `.fortnite (name) [platform (pc, xbl, psn)]`\n\n"
		help_message += " If no platform is specified, `pc` is default\n\n"
		yield from client.send_message(message.channel, help_message)
		return
	elif message.content.lower().startswith(".fortnite "):
		text = " ".join(message.content.split()).split()
		platform = "pc"
		name = ""

		if len(text) < 2:
			yield from client.send_message(message.channel, "Please supply a username (e.g. .fortnite youda)")
			return
		else:
			name = text[1]
			for x in text[2:len(text)]:
				arg = x.lower()
				if arg in ["pc", "xbl", "psn"]:
					platform = arg
				else:
					errormsg = "Invalid argument `" + arg + "`\nAccepted values for platform are (pc, xbl, psn)"
					yield from client.send_message(message.channel, errormsg)
					return
		embed = yield from get_stats_embed(name, platform)
		yield from client.send_message(message.channel, embed=embed)

client.run(DISCORD_TOKEN)
