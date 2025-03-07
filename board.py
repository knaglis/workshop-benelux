#!/usr/bin/env python3

import random
from config import boardSize, wordFull, symbolEmpty, symbolSpawnProbability

boardMax = boardSize * boardSize
walls = []

wordUnique = ''
for letter in wordFull:
  if letter not in wordUnique:
    wordUnique += letter

letterRepeat = 1

# Convert board list to string
def boardToStr(brd, fancy=False):
  retStr = ""
  for y in range(boardSize):
    for x in range(boardSize):
      if fancy:
        retStr += f'{brd[y][x]} '
      else:
        retStr += brd[y][x]
    if fancy:
      retStr += '\n'

  return retStr

# Convert string to board list
def strToBoard(boardStr):
  arrayBuffer = []

  subArrayBuffer = []
  counter = 0
  for current in range(boardMax):
    counter += 1
    subArrayBuffer.append(boardStr[current])

    if counter == boardSize:
      arrayBuffer.append(subArrayBuffer)
      subArrayBuffer = []
      counter = 0

  return arrayBuffer

# Build the initial board as a list
def build():
  generateWallsList()
  board = []
  for _ in range(boardSize):
    yLine = []
    for _ in range(boardSize):
      yLine.append(random.choice(walls))
    board.append(yLine)

  generateLetters(board)
  return board

# Generate walls on the board
def generateWallsList():
  for wallType in symbolSpawnProbability:
    probability = symbolSpawnProbability[wallType]
    for _ in range(probability):
      walls.append(wallType)

# Generate collectable letters on the board
def generateLetters(board):
  for letter in wordUnique:
    for _ in range(letterRepeat):
      found = False
      while not found:
        x = random.randrange(0, boardSize)
        y = random.randrange(0, boardSize)

        if board[y][x] == symbolEmpty:
          board[y][x] = letter
          found = True
