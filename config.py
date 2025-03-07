#!/usr/bin/env python3

# ==============================
# Zabbix configuration variables
# ==============================
zabbixServerIP = '127.0.0.1'
zabbixServerPort = 10051
zabbixAPIPath = f'{zabbixServerIP}/zabbix'
zabbixAdminToken = ''
zabbixPlayerToken = ''

# ==============================
# Game setup variables
# ==============================
playerHosts = [
  '127.0.0.1:8001',
]
playerCount = len(playerHosts)

masterHost = []
masterCount = len(masterHost)

hostgroupPathMaster = 'Workshop/Benelux'
hostgroupPathPlayer = f'{hostgroupPathMaster}/Player'
hostgroupPathGame = f'{hostgroupPathMaster}/Game'

# ==============================
# Game configuration variables
# ==============================
webServerIP = '0.0.0.0'
webServerPort = 8001
webServerPortMaster = 8002

gameMasterHostName = 'Main Game'
gameMasterHostId = None
gameMapKey = 'game.map'

playerPositionKey = f'player.position.{zabbixPlayerToken}'

boardSize = 40

wordFull = 'ZABBIX'

# Player and game board symbols
symbolCurrentPlayer = '@'
symbolPlayer = '*'
symbolEmpty = ' '

symbolsWalls = ['│', '─']
symbolSpawnProbability = {
  symbolEmpty: 17,
  symbolsWalls[0]: 1,
  symbolsWalls[1]: 1
}