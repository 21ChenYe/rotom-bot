#! usr/bin/python3

import discord, logging
from discord.utils import get
import bs4, requests, time


logging.basicConfig(level = logging.INFO)
client = discord.Client()

async def replayWinner(soup, message): #returns the winner of a pokemon showdown replay
	#finds string of winner
	indexWin = soup.get_text().find('|win|') 
	indexEnd = soup.get_text()[indexWin:].find('\n')
	winner = soup.get_text()[indexWin:][5:indexEnd]
	#initializes various index variables and counts amount of faints
	index1 = 0
	count = 0
	while True: #this loop counts instances of faint
		if soup.get_text()[index1:].find('|faint|') == -1:
			break
		elif soup.get_text()[index1:].find('|faint|') > 0:
			index1 = index1 + (soup.get_text()[index1:].find('|faint|') + 7)
			count += 1
	index1 = soup.get_text().find('replay:') #finds index of replay
	index2 = soup.get_text()[index1:].find('Pokémon') #finds index of Pokémon after replay
	victoryMessage = soup.get_text()[(index1+8):(index1+index2-2)] #finds (p1) vs (p2) message
	if soup.get_text().find('forfeited.') > 0: #if someone forfeited, do not record score
		await message.channel.send(victoryMessage + '/ Forfeit / ' + winner + ' wins' )
	else: #no one has forfeited, record score
		await message.channel.send(victoryMessage + '/ %s - 0 / ' %(12-count) + winner + ' wins' )	


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')
	#returns list of names with a specified role, usage is $rolelist (insert role here)
	elif message.content.startswith('$rolelist'):
		role = get(message.guild.roles, name= message.content[10:])
		for members in role.members:
			await message.channel.send(members.display_name)
	#checks for pokemon showdown replay and returns conclusion of battle
	elif message.content.find('replay.pokemonshowdown') > 1:
		page = requests.get(message.content)
		soup = bs4.BeautifulSoup(page.content, 'html.parser')
		await replayWinner(soup, message)

		
		
client.run('INSERT DISCORD BOT KEY HERE')
