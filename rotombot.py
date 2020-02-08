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
		image = table.findAll('img')[0]
		index1 = mhsoup.get_text().find('Weakness')
		index2 = mhsoup.get_text()[index1:].find('Resistances')
		weakMsg = mhsoup.get_text()[index1:][:index2].replace("\xa0"," ").replace("\n"," ").replace("(","").replace(")","");
		rindex = mhsoup.get_text()[index1+index2+12:].find('\n')
		resistMsg = mhsoup.get_text()[index1+index2+12:][:rindex]
		#find a thumbnail	
		try:
			imageLink = wikiLink + image['data-src']
		except:
			imageLink = wikiLink + image['src']

		speciesIndex1 = mhsoup.get_text().find('Species') + 8
		speciesIndex2 = mhsoup.get_text()[speciesIndex1:].find('\n')
		species = mhsoup.get_text()[speciesIndex1:speciesIndex1+speciesIndex2]

		embed=discord.Embed(title=monster.upper(), description=species, color=0x00ff1d)
		embed.set_thumbnail(url=imageLink)
		embed.add_field(name="Weakness", value=weakMsg[8:], inline=False)
		embed.add_field(name="Resistance", value=resistMsg, inline=False)

		temper = mhsoup.get_text().find('Tempered L')
		embed.set_footer(text=mhsoup.get_text()[temper:][:14].replace("\n"," "))
		
		
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
		page = requests.get('') #insert server link here
		if page.status_code == 200:
			await message.channel.send('Server is online!')
			await message.channel.send('') #insert server link here
		else:
			await message.channel.send('Server is not online')
	elif message.content.startswith('$mhweak'):
		monster = message.content[8:]
		await mhweak(monster, message)
		
client.run('') #insert key here
