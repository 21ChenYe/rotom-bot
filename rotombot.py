#! usr/bin/python3

import discord, logging
from discord.utils import get
import bs4, requests, time


logging.basicConfig(level = logging.INFO)
client = discord.Client()
fileKey = open("key.txt", 'r')
key = fileKey.readline()
server = fileKey.readline()
fileKey.close()
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

async def mhweak(monster, message):
	monster.replace(" ","+")
	wikiLink = 'https://monsterhunterworld.wiki.fextralife.com/'
	mhwiki = requests.get(wikiLink + monster)

	if mhwiki.status_code == 404:
		await message.channel.send('Invalid Entry!')
		return
	else: #past the error check stage
		mhsoup = bs4.BeautifulSoup(mhwiki.content, 'html.parser')
		table = mhsoup.findAll('table')[0]
		#Table Stringing Logic: Find indexes
		tableText = table.getText().replace('\n', ' ').replace('\xa0', ' ') #remove extraneous
		indexSpecies = tableText.find('Species') #can be -1
		indexElements = tableText.find('Elements') 
		indexAilments = tableText.find('Ailments')
		indexWeakness = tableText.find('Weakness') #account for spelling
		indexWeakEnd = tableText[indexWeakness:].find(' ')
		indexResistances = tableText.find('Resistances')
		indexLocations = tableText.find('Location') #account for spelling
		indexLocEnd = tableText[indexLocations:].find(' ')
		indexTempered = tableText.find('Tempered') #can be -1

		#use indexes to form messages
		if indexSpecies != -1:
			species = tableText[indexSpecies + 8: indexElements]
		else:
			species = '';

		elements = tableText[indexElements + 9: indexAilments]
		ailments = tableText[indexAilments + 9: indexWeakness]
		weakness = tableText[indexWeakness + indexWeakEnd: indexResistances]
		resistance = tableText[indexResistances + 12: indexLocations]
		locations = tableText[indexLocations + indexLocEnd: indexTempered]

		image = table.findAll('img')[0]
		#find a thumbnail	
		try:
			imageLink = wikiLink + image['data-src']
		except:
			imageLink = wikiLink + image['src']
			
		embed=discord.Embed(title=monster.upper(), description=species, color=0x00ff1d)
		embed.set_thumbnail(url=imageLink)

		embed.add_field(name="Elements", value=elements, inline=False)
		embed.add_field(name="Ailments", value=ailments, inline=False)
		embed.add_field(name="Weakness", value=weakness, inline=False)
		embed.add_field(name="Resistance", value=resistance, inline=False)
		embed.add_field(name="Locale", value=locations, inline=False)
		embed.set_footer(text=tableText[indexTempered:])
		
		await message.channel.send(embed=embed)

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
	elif message.content.startswith('$server'):
		page = requests.get(server)
		if page.status_code == 200:
			await message.channel.send('Server is online!')
			await message.channel.send(server)
		else:
			await message.channel.send('Server is not online')
	elif message.content.startswith('$mhbio'):
		monster = message.content[7:]
		await mhweak(monster, message)

client.run(key.replace('\n',''))
