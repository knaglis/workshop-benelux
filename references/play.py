#!/usr/bin/env python3

from zabbix_utils import AsyncZabbixAPI, AsyncSender
from http.server import HTTPServer, BaseHTTPRequestHandler
from helpers import AsyncMixin

import board
import time
import curses
import asyncio
import threading
import sys
import termios
import tty
import json
import config


zabbixGameMap = None
mapMaxChars = config.boardSize * config.boardSize


class ZabbixRequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    global zabbixGameMap

    if self.headers.get('Authorization') != f'Bearer {config.zabbixPlayerToken}':
      self.send_response(401)
      return

    self.send_response(200)
    self.end_headers()

    content_len = int(self.headers.get('Content-Length'))
    post_body = self.rfile.read(content_len)
    ndjson_content = post_body.decode()
    zabbixGameMap = json.loads(ndjson_content.splitlines()[-1])['value']

  # Disable log message prints to console
  def log_message(self, format, *args):
    return


class Zabbix(AsyncMixin):
  def __init__(self):
    super().__init__()
    # Initialize defaults
    self.playerHostId = None
    self.playerHostName = None
    self.playerPosition = [0, 0]
    self.counter = 0
    self.gameMap = ''
    self.score = ''

  async def __ainit__(self):
    # Initialize asynchronous defaults
    # ! IMPLEMENT - asynchronous Zabbix API object
    self.api = AsyncZabbixAPI(url=config.zabbixAPIPath, validate_certs=False)
    await self.apiLogin()
    await self.setPlayerHost()
    # ! IMPLEMENT - asynchronous Zabbix sender object
    self.sender = AsyncSender(server=config.zabbixServerIP, port=config.zabbixServerPort)

  # ! IMPLEMENT - API login method
  async def apiLogin(self):
    await self.api.login(token=config.zabbixPlayerToken)

  def setMap(self):
    global zabbixGameMap
    while True:
      if zabbixGameMap and len(zabbixGameMap) == mapMaxChars:
        gameMapObj = board.strToBoard(zabbixGameMap)
        gameMapObj[self.playerPosition[1]][self.playerPosition[0]] = config.symbolCurrentPlayer
        gameMapObj = board.boardToStr(gameMapObj, True)
        self.gameMap = gameMapObj.split('\n')
        time.sleep(0.1)

  def getMap(self) -> str:
    return self.gameMap

  # ! IMPLEMENT - request current player position
  async def setCurrentPosition(self) -> list:
    while True:
      currentPosition = await self.api.item.get(
        hostids=self.playerHostId,
        search={'key_': config.playerPositionKey},
        output=['lastvalue']
      )
      currentPosition = currentPosition[0]['lastvalue']
      currentPosition = str(currentPosition).split(' ')
      currentPosition[0] = int(currentPosition[0])
      currentPosition[1] = int(currentPosition[1])
      self.playerPosition = currentPosition
      await asyncio.sleep(0)

  def getCurrentPosition(self):
    return self.playerPosition

  # ! IMPLEMENT - request player host
  async def setPlayerHost(self):
    hosts = await self.api.host.get(
      search={'host': 'Player'},
      output=['host', 'hostid']
    )
    self.playerHostId = hosts[0]['hostid']
    self.playerHostName = hosts[0]['host']

  # ! IMPLEMENT - request score
  async def setScore(self):
    while True:
      self.score = (await self.api.item.get(
        search={'key_': 'player.score'},
        output=['lastvalue']
      ))[0]['lastvalue']
      await asyncio.sleep(0)

  def getScore(self):
    return self.score

  async def move(self, direction):
    # Get position
    position = self.playerPosition
    x = position[0]
    y = position[1]

    # Set coordinates for next position
    if direction == 119:
      y = position[1] - 1
    elif direction == 97:
      x = position[0] - 1
    elif direction == 115:
      y = position[1] + 1
    elif direction == 100:
      x = position[0] + 1
    else:
      return
    
    # ! IMPLEMENT - async Zabbix sender to send updated position values
    # Check if new position is not out of map and does not collide with a wall
    if 0 <= x < config.boardSize and 0 <= y < config.boardSize:
      cellValue = self.gameMap[y][x*2]
      if cellValue not in config.symbolsWalls:
        await self.sender.send_value(self.playerHostName, config.playerPositionKey, f'{x} {y}')


class UI:
  def __init__(self):
    self.word = ''

    self.calculateScreen()

    self.stdscr.nodelay(True)

    # Setup curses windows and a pad
    self.windowBorder = self.stdscr.subwin(13, 24, self.gameRowsMid - 1, self.gameColsMid - 1)
    self.windowScore = self.stdscr.subwin(1, 20, self.gameRowsMid - 2, self.gameColsMid)
    self.padMap = curses.newpad(config.boardSize + 2, (config.boardSize * 2) + 2)

    self.stdscr.clear()
    self.stdscr.refresh()

    self.controlKey = ''
    self.zabbixMap = ''
    self.playerPosition = [0, 0]

    self.windowBorder.border(0, 0, 0, 0, 0, 0, 0, 0)
    self.windowBorder.refresh()

  def calculateScreen(self):
    self.stdscr = curses.initscr()

    self.height, self.width = self.stdscr.getmaxyx()

    self.cols_tot = self.width
    self.rows_tot = self.height
    self.cols_mid = int(0.5*self.cols_tot)
    self.rows_mid = int(0.5*self.rows_tot)

    self.gameColsMid = int(self.cols_mid - 10)
    self.gameRowsMid = int(int(0.5*self.rows_tot) - (10 / 2))

    self.done: bool = False

  def erase1(self):
    self.padMap.erase()
    self.windowScore.erase()
    self.windowBorder.erase()
    self.stdscr.clear()

  def refresh1(self):
    self.windowScore.refresh()
    self.windowBorder.refresh()

    # Move map accordingly to player position ...
    posY = 0
    posX = 0
    # ... along X axis
    if self.playerPosition[1] + 6 > config.boardSize:
      posY = config.boardSize - 10
    else:
      posY = self.playerPosition[1] - 4
    # ... along Y axis
    if self.playerPosition[0] + 6 > config.boardSize:
      posX = (config.boardSize * 2) - 21
    else:
      posX = (self.playerPosition[0] * 2) - 9

    self.padMap.refresh(posY, posX, self.gameRowsMid, self.gameColsMid,self.gameRowsMid + 10, self.gameColsMid + 20)

    self.windowScore.addstr(0, 0, self.word)
    self.stdscr.refresh()

  def updateScreen(self):
    while True:
      # Check if screen size has changed since last update
      height, width = self.stdscr.getmaxyx()
      if height != self.height or width != self.width:
        self.calculateScreen()

      # Loop through map and add line by line
      gameMap = self.zabbixMap
      for line in range(len(gameMap) - 1):
        self.padMap.addstr(1 + line, 1, gameMap[line])

      self.refresh1()
      time.sleep(0.1)


class Game(AsyncMixin):
  def __init__(self):
    super().__init__()

  async def __ainit__(self):
    self.zabbix = await Zabbix()
    self.ui = UI()  # <--- uncomment this line

  def updateScreen(self):
    self.ui.updateScreen()

  def synchronizeData(self):
    while True:
      self.ui.zabbixMap = self.zabbix.getMap()
      self.ui.playerPosition = self.zabbix.getCurrentPosition()
      self.ui.word = self.zabbix.getScore()
      time.sleep(0.1)

  def getch(self):
    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    try:
      tty.setcbreak(fd)
      return sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSAFLUSH, orig)

  def askInput(self):
    while True:
      i = self.getch()
      self.ui.controlKey = i

  async def movePlayer(self):
    while True:
      if self.ui.controlKey != '':
        await self.zabbix.move(ord(self.ui.controlKey))
        self.ui.controlKey = ''
      await asyncio.sleep(0)

  async def movePlayerNoUI(self):
    while True:
      await self.zabbix.move(ord(self.getch()))
      await asyncio.sleep(0.5)

  def startHttpServer(self):
    with HTTPServer((config.webServerIP, config.webServerPort), ZabbixRequestHandler) as server:
      server.serve_forever()

  async def run(self):
    try:
      """"""
      threadHTTP = threading.Thread(target=self.startHttpServer)
      threadHTTP.start()

      time.sleep(2)

      threadSetMap = threading.Thread(target=self.zabbix.setMap)
      threadSetMap.start()

      threadUiUpdate = threading.Thread(target=self.updateScreen)
      threadUiUpdate.start()

      threadSync = threading.Thread(target=self.synchronizeData)
      threadSync.start()

      threadInput = threading.Thread(target=self.askInput)
      threadInput.start()

      # ! IMPLEMENT - launch multiple functions with asyncio
      await asyncio.gather(self.zabbix.setCurrentPosition(), self.movePlayer(), self.zabbix.setScore())

    except Exception as e:
      print(f'[ EXCEPTION ]: {e}')
      await self.zabbix.api.logout()


async def runGame():
  game = await Game()
  await game.run()

if __name__ == "__main__":
  try:
    """"""
    # ! IMPLEMENT - run the asynchronous coroutine
    asyncio.run(runGame())
  except Exception as e:
    print(f'[ EXCEPTION ]: {e}')
    exit(1)
