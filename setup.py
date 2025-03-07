#!/usr/bin/env python3

from zabbix_utils import ZabbixAPI, Sender
import argparse
import json
import time
import random
import string
import secrets
import config


# ! IMPLEMENT - Create Zabbix API object and authenticate
api = ZabbixAPI(url=config.zabbixAPIPath, validate_certs=False)
api.login(token=config.zabbixAdminToken)


def generateLocations():
  return [(random.randint(0, config.boardSize - 1), random.randint(0, config.boardSize - 1)) for i in range(config.playerCount)]

# =============================================================================
# Users
# =============================================================================
def getUsers():
  print('Getting users')
  users = api.user.get(
    search={'username': 'Player'},
    output=['username', 'userid']
  )
  buffer = []
  for user in users:
    buffer.append({'name': user['username'], 'id': user['userid']})
  return buffer


def removeUsers(users):
  print('Removing users')
  if len(users) == 0:
    print('No existing player users found. Skipping delete...\n')
    return

  buffer = []
  for user in users:
    buffer.append(user['id'])

  api.user.delete(buffer)
  print('Player users removed\n')


def addUsers(roleId):
  print('Adding users')

  buffer = {}
  alphabet = string.ascii_letters + string.digits

  users = []
  for player in range(1, config.playerCount + 1):
    users.append({
      'username': f'Player {player}',
      'passwd': ''.join(secrets.choice(alphabet) for i in range(20)),
      'roleid': int(roleId)
    })

  print(f'\tAdding player users')
  createdUsers = api.user.create(users)

  for idx, userid in enumerate(createdUsers['userids']):
    buffer[f'Player {idx + 1}'] = userid

  print('Player users added\n')
  return buffer


# =============================================================================
# User groups
# =============================================================================
def getUserGroups():
  print('Getting user groups')
  userGroups = api.usergroup.get(
    search={'name': 'Player'},
    output=['usrgrpid']
  )
  buffer = []
  for userGroup in userGroups:
    buffer.append(userGroup['usrgrpid'])
  return buffer


def removeUserGroups(userGroups):
  if len(userGroups) == 0:
    print('No existing player user groups found. Skipping delete...\n')
    return
  api.usergroup.delete(userGroups)
  print('Player user groups removed\n')


def addUserGroups(users):
  print('Adding player user groups')
  hostGroups = getHostGroups(['groupid', 'name'], config.hostgroupPathMaster)
  gameHostGroupId = None
  for hostGroup in hostGroups:
    if hostGroup['name'] == f'{config.hostgroupPathMaster}/Game':
      gameHostGroupId = hostGroup['groupid']

  for player in range(1, config.playerCount + 1):
    playerHostGroupId = None
    for hostGroup in hostGroups:
      if hostGroup['name'] == f'{config.hostgroupPathMaster}/Player/{player}':
        playerHostGroupId = hostGroup['groupid']

    api.usergroup.create(
      name=f'Player {player}',
      users=[{'userid': users[f'Player {player}']}],
      hostgroup_rights=[
        {
          'id': playerHostGroupId,
          'permission': 2
        },
        {
          'id': gameHostGroupId,
          'permission': 2
        }
      ]
    )
  print('Player user groups added\n')


# =============================================================================
# Roles
# =============================================================================
def getRoles():
  print('Getting players role')
  roles = api.role.get(
    search={'name': 'Players'},
    output=['roleid']
  )

  buffer = []
  for role in roles:
    buffer.append(role['roleid'])
  return buffer


def removeRoles(roles):
  print('Removing players role')
  if len(roles) == 0:
    print('No existing player roles found. Skipping delete...\n')
    return
  api.role.delete(roles)
  print('Players role removed\n')


def addRole():
  print('Adding players role')
  roleid = api.role.create(
    name=f'Players',
    type=1,
    rules={
      "ui": [
        {
          "name": "monitoring.hosts",
          "status": "1"
        },
        {
          "name": "monitoring.dashboard",
          "status": "0"
        },
        {
          "name": "monitoring.problems",
          "status": "0"
        },
        {
          "name": "monitoring.latest_data",
          "status": "0"
        },
        {
          "name": "monitoring.maps",
          "status": "0"
        },
        {
          "name": "services.services",
          "status": "0"
        },
        {
          "name": "services.sla_report",
          "status": "0"
        },
        {
          "name": "inventory.overview",
          "status": "0"
        },
        {
          "name": "inventory.hosts",
          "status": "0"
        },
        {
          "name": "reports.availability_report",
          "status": "0"
        },
        {
          "name": "reports.top_triggers",
          "status": "0"
        }
      ],
      "ui.default_access": "0",
      "services.read.mode": "0",
      "services.read.list": [],
      "services.read.tag": {
        "tag": "",
        "value": ""
      },
      "services.write.mode": "0",
      "services.write.list": [],
      "services.write.tag": {
        "tag": "",
        "value": ""
      },
      "modules": [
        {
          "moduleid": 1,
          "status": "0"
        },
        {
          "moduleid": 2,
          "status": "0"
        },
        {
          "moduleid": 3,
          "status": "0"
        },
        {
          "moduleid": 4,
          "status": "0"
        },
        {
          "moduleid": 5,
          "status": "0"
        },
        {
          "moduleid": 6,
          "status": "0"
        },
        {
          "moduleid": 7,
          "status": "0"
        },
        {
          "moduleid": 8,
          "status": "0"
        },
        {
          "moduleid": 9,
          "status": "0"
        },
        {
          "moduleid": 10,
          "status": "0"
        },
        {
          "moduleid": 11,
          "status": "0"
        },
        {
          "moduleid": 12,
          "status": "0"
        },
        {
          "moduleid": 13,
          "status": "0"
        },
        {
          "moduleid": 14,
          "status": "0"
        },
        {
          "moduleid": 15,
          "status": "0"
        },
        {
          "moduleid": 16,
          "status": "0"
        },
        {
          "moduleid": 17,
          "status": "0"
        },
        {
          "moduleid": 18,
          "status": "0"
        },
        {
          "moduleid": 19,
          "status": "0"
        },
        {
          "moduleid": 20,
          "status": "0"
        },
        {
          "moduleid": 21,
          "status": "0"
        },
        {
          "moduleid": 22,
          "status": "0"
        },
        {
          "moduleid": 23,
          "status": "0"
        },
        {
          "moduleid": 24,
          "status": "0"
        },
        {
          "moduleid": 25,
          "status": "0"
        },
        {
          "moduleid": 26,
          "status": "0"
        },
        {
          "moduleid": 27,
          "status": "0"
        },
        {
          "moduleid": 28,
          "status": "0"
        },
        {
          "moduleid": 29,
          "status": "0"
        },
        {
          "moduleid": 30,
          "status": "0"
        }
      ],
      "modules.default_access": "0",
      "api.access": "1",
      "api.mode": "1",
      "api": [
        "host.get",
        "item.get"
      ],
      "actions": [
        {
          "name": "edit_dashboards",
          "status": "0"
        },
        {
          "name": "edit_maps",
          "status": "0"
        },
        {
          "name": "acknowledge_problems",
          "status": "0"
        },
        {
          "name": "suppress_problems",
          "status": "0"
        },
        {
          "name": "close_problems",
          "status": "0"
        },
        {
          "name": "change_severity",
          "status": "0"
        },
        {
          "name": "add_problem_comments",
          "status": "0"
        },
        {
          "name": "execute_scripts",
          "status": "0"
        },
        {
          "name": "manage_api_tokens",
          "status": "0"
        },
        {
          "name": "invoke_execute_now",
          "status": "0"
        },
        {
          "name": "change_problem_ranking",
          "status": "0"
        }
      ],
      "actions.default_access": "0"
    }
  )
  print('Players role added\n')
  return roleid['roleids'][0]

# =============================================================================
# Tokens
# =============================================================================


def getTokens():
  print('Getting tokens')
  tokens = api.token.get(
    search={'name': 'Player'},
    output=['tokenid', 'name']
  )
  buffer = []
  for token in tokens:
    buffer.append(token['tokenid'])
  return buffer


def removeTokens(tokens):
  print('Removing tokens')
  if len(tokens) == 0:
    print('No existing player tokens found. Skipping delete...\n')
    return

  api.token.delete(tokens)
  print('Player tokens removed\n')


def addTokens(users):
  print('Adding player tokens')

  buffer = []
  for user in users:
    buffer.append({'name': user, 'userid': users[user]})

  tokens = api.token.create(buffer)

  returnBuffer = {}
  for idx, user in enumerate(users):
    returnBuffer[user] = tokens['tokenids'][idx]

  print('Added player tokens\n')
  return returnBuffer


def generateTokens(tokens):
  print('Generating player tokens')

  tokenIds = []
  for token in tokens:
    tokenIds.append(tokens[token])

  generatedTokens = api.token.generate(tokenIds)

  buffer = {}
  for token in tokens:
    for genToken in generatedTokens:
      if genToken['tokenid'] == tokens[token]:
        buffer[token] = genToken['token']
        print(f'"{genToken["token"]}",')

  # write tokens to file
  f = open('playerTokens', 'w')
  f.write(json.dumps(buffer))
  f.write(f'\n')
  f.close()

  print('Generated player tokens\n')
  return buffer


# =============================================================================
# Hosts
# =============================================================================
def getHosts(name, out: list):
  print('Getting hosts')
  return api.host.get(
    search={'name': name},
    output=out
  )
  # buffer = []
  # for host in playerHosts:
  #   buffer.append(host['name'])
  # return buffer

# defender


def removeHosts(hosts):
  print('Removing hosts')
  if len(hosts) > 0:
    hostsBuffer = []
    for host in hosts:
      hostsBuffer.append(host['hostid'])

    api.host.delete(hostsBuffer)
    print('Hosts removed\n')
  else:
    print('No existing hosts found. Skipping delete...\n')


def addHostsPlayer():
  print('Adding player hosts')
  hostGroups = getHostGroups(['groupid', 'name'], config.hostgroupPathPlayer)

  hostsBuffer = []
  for player in range(1, config.playerCount + 1):
    hostsBuffer.append({'host': f'Player {player}', 'groups': [{'groupid': [
               hostGroup for hostGroup in hostGroups if hostGroup.get('name') == f'{config.hostgroupPathPlayer}/{player}'][0]['groupid']}]})

  addedHosts = api.host.create(hostsBuffer)

  for idx, host in enumerate(hostsBuffer):
    host['hostid'] = addedHosts['hostids'][idx]

  print('Added player hosts\n')
  return hostsBuffer


def addHostsGame():
  print('Adding game hosts')

  hostGroups = getHostGroups(['groupid', 'name'], config.hostgroupPathGame)
  hostObject = [{
    'host': 'Main Game',
    'groups': [{
      'groupid': int(hostGroups[0]['groupid'])
    }]
  }]
  addedHosts = api.host.create(hostObject)

  hostObject[0]['hostid'] = addedHosts['hostids'][0]

  print('Added game hosts\n')
  return hostObject


# =============================================================================
# Host groups
# =============================================================================
def getHostGroups(params: list, path: str):
  return api.hostgroup.get(
    search={'name': path},
    output=params
  )

# defender


def removeHostGroups(hostGroups):
  if len(hostGroups) > 0:
    hostGroupsBuffer = []
    for hostGroup in hostGroups:
      hostGroupsBuffer.append(hostGroup['groupid'])

    api.hostgroup.delete(hostGroupsBuffer)
    print('Host groups removed\n')
  else:
    print('No existing host groups found. Skipping delete...\n')


def addHostGroups():
  print('Adding host groups')

  print('-Adding main host group')
  api.hostgroup.create(
    name=f'{config.hostgroupPathMaster}'
  )

  print('-Adding game host group')
  api.hostgroup.create(
    name=f'{config.hostgroupPathGame}'
  )

  print('-Adding player host groups')
  for player in range(1, config.playerCount + 1):
    api.hostgroup.create(
      name=f'{config.hostgroupPathPlayer}/{player}'
    )

  print('Host groups added\n')

# =============================================================================
# Items
# =============================================================================


def getItems(name, params: list):
  print(f'Getting items | name: {name} | params: {params}')
  return api.item.get(
    search={'name': name},
    output=params
  )


def createItemsPlayer(hosts, tokens):
  print('Creating player items')
  itemsBuffer = []
  for host in hosts:
    print(f'\tfor {host["host"]}')
    itemkey = f'player.position.{tokens[host["host"]]}'
    itemObj = {
      'name': 'Position',
      'key_': itemkey,
      'hostid': host['hostid'],
      'type': 2,
      'value_type': 1
    }
    itemsBuffer.append(itemObj)
    host['posItemKey'] = itemkey

    itemObj = {
      'name': 'Score',
      'key_': 'player.score',
      'hostid': host['hostid'],
      'type': 2,
      'value_type': 1
    }
    itemsBuffer.append(itemObj)

  api.item.create(itemsBuffer)
  print('Done creating player items\n')
  return hosts


def createItemsGame(host):
  print('Creating game items')
  api.item.create({
    'name': 'Map',
    'key_': 'game.map',
    'hostid': host[0]['hostid'],
    'type': 2,
    'value_type': 4,
    'tags': [
      {
        'tag': 'game',
        'value': 'map'
      }
    ]
  })
  print('Done creating game items\n')


def populatePlayerHostItems(items):
  print('Populating player items')
  playerCoordinates = generateLocations()

  sender = Sender(server=config.zabbixServerIP, port=config.zabbixServerPort)
  for item in items:
    hostNumber = int(item['host'].split(' ')[1]) - 1
    coordinates = f'{playerCoordinates[hostNumber][1]} {playerCoordinates[hostNumber][0]}'

    print(
      f'\tsending host: {item["host"]} | item: {item["posItemKey"]} = {coordinates}')
    resp = sender.send_value(item['host'], item['posItemKey'], coordinates)
    print(f'\tresponse: {resp}\n')

  print('Done populating player items\n')


# =============================================================================
# Connectors
# =============================================================================
def getConnectors():
  print('Getting connectors')
  connectors = api.connector.get(
    output=['connectorid']
  )
  buffer = []
  for connector in connectors:
    buffer.append(connector['connectorid'])
  print('Done getting connectors\n')
  return buffer

# defender
def removeConnectors(connectors):
  print('Removing connectors')
  if len(connectors) > 0:
    api.connector.delete(connectors)
  else:
    print('No connectors found. Skipping delete...\n')
    return
  print('Done removing connectors\n')


def addConnectors(tokens):
  print('Adding connectors')

  buffer = []
  for master in range(config.masterCount):
    connectorName = f'Master {master + 1}'
    connectorUrl = f'http://{config.masterHost[master]}'
    connectorAuth = tokens[connectorName]
    buffer.append(generateConnectorItem(
      connectorName, connectorUrl, connectorAuth))
  for player in range(config.playerCount):
    connectorName = f'Player {player + 1}'
    connectorUrl = f'http://{config.playerHosts[player]}'
    connectorAuth = tokens[connectorName]
    buffer.append(generateConnectorItem(
      connectorName, connectorUrl, connectorAuth))

  api.connector.create(buffer)
  print('Done adding connectors\n')

# returns a list with correct connector properties


def generateConnectorItem(name: str, url: str, token: str):
  return {
    'name': name,
    'url': url,
    'tags': [{
      'tag': 'game',
      'operator': 0,
      'value': 'map'
    }],
    'data_type': 0,
    'max_senders': 1,
    'max_attempts': 1,
    'timeout': '3s',
    'authtype': 5,
    'token': token
  }


# =============================================================================
# Main
# =============================================================================
def completeReset():
  # Users
  oldUsers = getUsers()
  removeUsers(oldUsers)

  # Roles
  roles = getRoles()
  removeRoles(roles)
  newRoleId = addRole()

  newUsers = addUsers(newRoleId)

  # Hosts
  hostsPlayer = getHosts('Player', ['hostid', 'name'])
  removeHosts(hostsPlayer)
  hostsGame = getHosts('Main Game', ['hostid', 'name'])
  removeHosts(hostsGame)

  # Host groups
  hostGroupMaster = getHostGroups(['groupid'], config.hostgroupPathMaster)
  removeHostGroups(hostGroupMaster)

  hostGroupPlayers = getHostGroups(['groupid'], config.hostgroupPathPlayer)
  removeHostGroups(hostGroupPlayers)

  hostGroupGame = getHostGroups(['groupid'], config.hostgroupPathGame)
  removeHostGroups(hostGroupGame)

  addHostGroups()

  playerHosts = addHostsPlayer()
  gameHost = addHostsGame()

  # User groups
  userGroups = getUserGroups()
  removeUserGroups(userGroups)
  addUserGroups(newUsers)

  # Tokens
  oldTokens = getTokens()
  removeTokens(oldTokens)
  newTokens = addTokens(newUsers)
  tokens = generateTokens(newTokens)

  # Items
  itemsPlayer = createItemsPlayer(playerHosts, tokens)
  itemsGame = createItemsGame(gameHost)

  time.sleep(5)

  populatePlayerHostItems(itemsPlayer)

  # Connectors
  connectors = getConnectors()
  removeConnectors(connectors)
  addConnectors(tokens)


def positionReset():
  hosts = getHosts('Player', ['hostid', 'name'])
  items = getItems('Position', ['hostid', 'key_'])
  buffer = []
  for host in hosts:
    found = next(
      item for item in items if item['hostid'] == host['hostid'])
    tmp = {}
    tmp['host'] = host['name']
    tmp['posItemKey'] = found['key_']
    buffer.append(tmp)
  populatePlayerHostItems(buffer)


def cmd_args_parser():
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)

  group.add_argument('-f', '--full', dest='actionFull',
             action='store_true', help='Do a full setup.')
  group.add_argument('-p', '--position', dest='actionPartial',
             action='store_true', help='Reset player positions.')
  args = parser.parse_args()

  if args.actionFull is True:
    completeReset()
  elif args.actionPartial is True:
    positionReset()
  else:
    print('Incorrect argument passed.')
    exit(1)


if __name__ == '__main__':
  cmd_args_parser()
