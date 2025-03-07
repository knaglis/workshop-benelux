#!/usr/bin/env python3

from zabbix_utils import ZabbixAPI, Sender
from copy import deepcopy
import time
import board
import threading
import config

api = ZabbixAPI(url=config.zabbixAPIPath)
api.login(token=config.zabbixAdminToken)

sender = Sender(server=config.zabbixServerIP, port=config.zabbixServerPort)

wordFullLength = len(config.wordFull)


class Backend:
  def __init__(self, startingBoard):
    self.startingBoard = startingBoard
    self.board = None
    self.locations = None
    self.scores = {}

  def getPlayerLocations(self):
    while True:
      # get player locations
      self.locations = api.item.get(
        search={'name': 'Position'},
        output=['hostid', 'lastvalue'],
        selectHosts='extend'
      )

  def parsePlayerLocations(self):
    while True:
      tempBoard = deepcopy(self.startingBoard)

      for location in self.locations:
        coordinates = location['lastvalue']
        if coordinates != '':
          coordinates = coordinates.split(' ')
          x = int(coordinates[0])
          y = int(coordinates[1])

          # Check if next move is not out of map
          if x < 0:
            x = 0
          elif x > config.boardSize - 1:
            x =  config.boardSize - 1

          if y < 0:
            y = 0
          elif y >  config.boardSize - 1:
            y =  config.boardSize - 1

          tempBoard[y][x] = config.symbolPlayer

      self.board = tempBoard
      time.sleep(0.1)

  def resetScores(self):
    # Initialize scores
    for location in self.locations:
      hostname = location['hosts'][0]['host']
      coordinates = location['lastvalue']
      if coordinates != '':
        self.scores[hostname] = []
        for _ in range(wordFullLength):
          self.scores[hostname].append('_')

  def parseScores(self):
    self.resetScores()
    while True:
      for location in self.locations:
        hostname = location['hosts'][0]['host']
        coordinates = location['lastvalue']
        if coordinates != '':
          coordinates = coordinates.split(' ')
          currentSymbol = self.startingBoard[int(coordinates[1])][int(coordinates[0])]
          if currentSymbol in config.wordFull:
            index = config.wordFull.index(currentSymbol)
            if index == 2:
              self.scores[hostname][index] = config.wordFull[index]
              self.scores[hostname][index + 1] = config.wordFull[index]
            else:
              self.scores[hostname][index] = config.wordFull[index]
        time.sleep(0.5)

  def updateScores(self):
    while True:
      for host in self.scores:
        sender.send_value(host, 'player.score', str(' '.join(self.scores[host])))
      time.sleep(0.25)

  def updateGameMap(self):
    while True:
      # update game board
      sender.send_value(config.gameMasterHostName,config.gameMapKey, board.boardToStr(self.board, False))
      time.sleep(0.25)

  def main(self):
    t1 = threading.Thread(target=self.getPlayerLocations)
    t2 = threading.Thread(target=self.parsePlayerLocations)
    t3 = threading.Thread(target=self.updateGameMap)
    t4 = threading.Thread(target=self.parseScores)
    t5 = threading.Thread(target=self.updateScores)

    t1.start()
    time.sleep(2)
    t2.start()
    time.sleep(1)
    t3.start()
    t4.start()
    time.sleep(1)
    t5.start()


if __name__ == "__main__":
  try:
    print('Backend script running')
    startingBoard = board.build()
    response = sender.send_value(config.gameMasterHostName, config.gameMapKey, board.boardToStr(startingBoard))

    backend = Backend(startingBoard)
    backend.main()
  except Exception as e:
    print(f'[ Exception ]: {e}')
    exit(1)
