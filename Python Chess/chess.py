import pygame, sys
import time
import pygame.font
import numpy as np
from pygame.locals import *
from string import ascii_lowercase
from itertools import product

pygame.init()


FPS = 30
FramePerSec = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)

screen_height = 800
screen_width = 800
margin = 5
screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
screen.fill(black)
pygame.display.set_caption("Chess")

stalemate = False
white_check = False
white_checkmate = False
black_check = False
black_checkmate = False

bpawn_promotion = None
wpawn_promotion = None

selected_piece = None
mouse_check = 0

current_coordinate = None

def drawGrid():
	global x_coordinates
	global y_coordinates
	global squareSize
	x_coordinates = np.array([])
	y_coordinates = np.array([])

	np.array(list(x_coordinates).clear())
	np.array(list(y_coordinates).clear())
	screenHeight = pygame.display.get_window_size()[1]
	screenWidth = pygame.display.get_window_size()[0]
	if screenWidth > screenHeight:
		font_size = round(screenHeight / 26)
	else:
		font_size = round(screenWidth / 26)
	font = pygame.font.SysFont('Arial', int(font_size))
	grid_pattern = 1
	if (screenHeight > screenWidth):
		squareSize = screenWidth / 12
	else:
		squareSize = screenHeight / 12
	pygame.draw.rect(screen, black, [(squareSize + ((((screenWidth / squareSize) - 8) / 2) * squareSize)) - squareSize - 0.1 * squareSize,
			 squareSize * 2 - 0.1 * squareSize, (8 * squareSize + 0.2 * squareSize), (8 * squareSize + 0.2 * squareSize)])
	for row in range(0, 8):
		text_surface = font.render(f"   {row + 1}", True, black)
		screen.blit(text_surface, ((squareSize + (((((screenWidth / squareSize) - 8) / 2) - 2) * squareSize)),
			 squareSize * row + (squareSize * 2.2)))
		y_position = squareSize * row + (squareSize * 2)
		y_coordinates = np.append(y_coordinates, y_position)
		for column in range(0,8):
			if grid_pattern % 2:
				colour = (white)
			else:
				colour = (black)
			x_position = (squareSize * column + (((screenWidth / squareSize) - 8) / 2) * squareSize)
			pygame.draw.rect(screen, colour, [x_position, y_position, squareSize, squareSize])

			if (row == 0):
				x_coordinates = np.append(x_coordinates, x_position)

			grid_pattern = grid_pattern + 1

		for column in range(0, 8):
			text_surface = font.render(f"  {ascii_lowercase[column]}", True, black)
			screen.blit(text_surface, (squareSize * column + ((((screenWidth / squareSize) - 8) / 2) * squareSize), squareSize*1.25))

		grid_pattern = grid_pattern - 1

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


class Piece:
	piece_list = []
	def __init__(self, image, name, colour, piece, x_coordinate, y_coordinate, x_position, y_position, active, unique_move, en_passant, simulated_x, simulated_y, value):
		self.image = image
		self.name = name
		self.colour = colour
		self.piece = piece
		self.x_coordinate = x_coordinate
		self.y_coordinate = y_coordinate
		self.x_position = x_position
		self.y_position = y_position
		self.active = active
		self.unique_move = unique_move
		self.en_passant = en_passant
		self.simulated_x = simulated_x
		self.simulated_y = simulated_y
		self.potential_move = []
		self.piece_list.append(self)

def potentialMoves(simulated_piece):
	if simulated_piece.active == True:
		for i in range(0, 8):
			for j in range(0, 8):
				potential_move = False
				if simulated_piece.colour == "white":
					if simulated_piece.piece == "pawn":
						if (i == simulated_piece.x_coordinate and j == simulated_piece.y_coordinate - 1) or (simulated_piece.unique_move == 1 and i == simulated_piece.x_coordinate and j == simulated_piece.y_coordinate - 2):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if i == piece.x_coordinate and j == piece.y_coordinate:
										potential_move = False
						for piece in Piece.piece_list:
							if piece != simulated_piece:
								if (i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and j == simulated_piece.y_coordinate - 1 and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = True
									if piece.colour == "white":
										potential_move = False
								elif piece.en_passant == True and (i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and j == simulated_piece.y_coordinate - 1 and (simulated_piece.x_coordinate + 1 == piece.x_coordinate or simulated_piece.x_coordinate - 1 == piece.x_coordinate) and simulated_piece.y_coordinate == piece.y_coordinate and i == piece.x_coordinate:
									potential_move = True
									if piece.colour == "white":
										potential_move = False		
					elif simulated_piece.piece == "knight":
						if ((i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and (j == simulated_piece.y_coordinate + 2 or j == simulated_piece.y_coordinate - 2) or (i == simulated_piece.x_coordinate + 2 or i == simulated_piece.x_coordinate - 2) and (j == simulated_piece.y_coordinate + 1 or j == simulated_piece.y_coordinate - 1)):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
					elif simulated_piece.piece == "king":
						if (-1 <= i - simulated_piece.x_coordinate <= 1) and (-1 <= j - simulated_piece.y_coordinate <= 1):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
						elif simulated_piece.unique_move == 1:
							if ((simulated_piece.x_coordinate + 2 == i) and simulated_piece.y_coordinate == j and Piece.piece_list[19].unique_move == 1):
								potential_move = True
								for piece in Piece.piece_list:
									if piece != simulated_piece:
										if (piece.y_coordinate == simulated_piece.y_coordinate) and (simulated_piece.x_coordinate <= piece.x_coordinate <= i):
											potential_move = False
							elif (simulated_piece.x_coordinate - 2 == i) and simulated_piece.y_coordinate == j and Piece.piece_list[17].unique_move == 1:
								potential_move = True
								for piece in Piece.piece_list:
									if piece != simulated_piece:
										if (piece.y_coordinate == simulated_piece.y_coordinate) and (simulated_piece.x_coordinate >= piece.x_coordinate >= i):
											potential_move = False
					elif simulated_piece.piece == "bishop":
						if (simulated_piece.x_coordinate - i == simulated_piece.y_coordinate - j or simulated_piece.x_coordinate - i == j - simulated_piece.y_coordinate or simulated_piece.y_coordinate - j == simulated_piece.x_coordinate - i or simulated_piece.y_coordinate - j == i - simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.active == True:
									if (i < piece.x_coordinate < simulated_piece.x_coordinate):
										if ((simulated_piece.x_coordinate - piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate) or (simulated_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate)) and ((piece.x_coordinate - i == piece.y_coordinate - j) or (piece.x_coordinate - i == j - piece.y_coordinate)):
											potential_move = False
									elif (i > piece.x_coordinate > simulated_piece.x_coordinate):
										if ((piece.x_coordinate - simulated_piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate) or (piece.x_coordinate - simulated_piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate)) and ((i - piece.x_coordinate == j - piece.y_coordinate) or (i - piece.x_coordinate == piece.y_coordinate - j)):
											potential_move = False
								if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
					elif simulated_piece.piece == "rook":
						if ((i > simulated_piece.x_coordinate or i < simulated_piece.x_coordinate) and j == simulated_piece.y_coordinate) or ((j > simulated_piece.y_coordinate or j < simulated_piece.y_coordinate) and i == simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if piece.active == True:
										if j == simulated_piece.y_coordinate == piece.y_coordinate:
											if (i < piece.x_coordinate < simulated_piece.x_coordinate) or (i > piece.x_coordinate > simulated_piece.x_coordinate):
												potential_move = False
										elif i == simulated_piece.x_coordinate == piece.x_coordinate:
											if (j < piece.y_coordinate < simulated_piece.y_coordinate) or (j > piece.y_coordinate > simulated_piece.y_coordinate):
												potential_move = False
										if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
											potential_move = False
					elif simulated_piece.piece == "queen":
						if ((i > simulated_piece.x_coordinate or i < simulated_piece.x_coordinate) and j == simulated_piece.y_coordinate) or ((j > simulated_piece.y_coordinate or j < simulated_piece.y_coordinate) and i == simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if piece.active == True:
										if j == simulated_piece.y_coordinate == piece.y_coordinate:
											if (i < piece.x_coordinate < simulated_piece.x_coordinate) or (i > piece.x_coordinate > simulated_piece.x_coordinate):
												potential_move = False
										elif i == simulated_piece.x_coordinate == piece.x_coordinate:
											if (j < piece.y_coordinate < simulated_piece.y_coordinate) or (j > piece.y_coordinate > simulated_piece.y_coordinate):
												potential_move = False
										if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
											potential_move = False
						elif (simulated_piece.x_coordinate - i == simulated_piece.y_coordinate - j or simulated_piece.x_coordinate - i == j - simulated_piece.y_coordinate or simulated_piece.y_coordinate - j == simulated_piece.x_coordinate - i or simulated_piece.y_coordinate - j == i - simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.active == True:
									if (i < piece.x_coordinate < simulated_piece.x_coordinate):
										if ((simulated_piece.x_coordinate - piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate) or (simulated_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate)) and ((piece.x_coordinate - i == piece.y_coordinate - j) or (piece.x_coordinate - i == j - piece.y_coordinate)):
											potential_move = False
									elif (i > piece.x_coordinate > simulated_piece.x_coordinate):
										if ((piece.x_coordinate - simulated_piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate) or (piece.x_coordinate - simulated_piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate)) and ((i - piece.x_coordinate == j - piece.y_coordinate) or (i - piece.x_coordinate == piece.y_coordinate - j)):
											potential_move = False
								if piece.colour == "white" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False

				if simulated_piece.colour == "black":
					if simulated_piece.piece == "pawn":
						if (i == simulated_piece.x_coordinate and j == simulated_piece.y_coordinate + 1) or (simulated_piece.unique_move == 1 and i == simulated_piece.x_coordinate and j == simulated_piece.y_coordinate + 2):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if i == piece.x_coordinate and j == piece.y_coordinate:
										potential_move = False
						for piece in Piece.piece_list:
							if piece != simulated_piece:
								if (i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and j == simulated_piece.y_coordinate + 1 and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = True
									if piece.colour == "black":
										potential_move = False
								elif piece.en_passant == True and (i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and j == simulated_piece.y_coordinate + 1 and (simulated_piece.x_coordinate + 1 == piece.x_coordinate or simulated_piece.x_coordinate - 1 == piece.x_coordinate) and simulated_piece.y_coordinate == piece.y_coordinate and i == piece.x_coordinate:
									potential_move = True
									if piece.colour == "black":
										potential_move = False	
					elif simulated_piece.piece == "knight":
						if ((i == simulated_piece.x_coordinate + 1 or i == simulated_piece.x_coordinate - 1) and (j == simulated_piece.y_coordinate + 2 or j == simulated_piece.y_coordinate - 2) or (i == simulated_piece.x_coordinate + 2 or i == simulated_piece.x_coordinate - 2) and (j == simulated_piece.y_coordinate + 1 or j == simulated_piece.y_coordinate - 1)):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
					elif simulated_piece.piece == "king":
						if (-1 <= i - simulated_piece.x_coordinate <= 1) and (-1 <= j - simulated_piece.y_coordinate <= 1):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
						elif simulated_piece.unique_move == 1:
							if ((simulated_piece.x_coordinate + 2 == i) and simulated_piece.y_coordinate == j and Piece.piece_list[18].unique_move == 1):
								potential_move = True
								for piece in Piece.piece_list:
									if piece != simulated_piece:
										if (piece.y_coordinate == simulated_piece.y_coordinate) and (simulated_piece.x_coordinate <= piece.x_coordinate <= i):
											potential_move = False
							elif (simulated_piece.x_coordinate - 2 == i) and simulated_piece.y_coordinate == j and Piece.piece_list[16].unique_move == 1:
								potential_move = True
								for piece in Piece.piece_list:
									if piece != simulated_piece:
										if (piece.y_coordinate == simulated_piece.y_coordinate) and (simulated_piece.x_coordinate >= piece.x_coordinate >= i):
											potential_move = False
					elif simulated_piece.piece == "bishop":
						if (simulated_piece.x_coordinate - i == simulated_piece.y_coordinate - j or simulated_piece.x_coordinate - i == j - simulated_piece.y_coordinate or simulated_piece.y_coordinate - j == simulated_piece.x_coordinate - i or simulated_piece.y_coordinate - j == i - simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.active == True:
									if (i < piece.x_coordinate < simulated_piece.x_coordinate):
										if ((simulated_piece.x_coordinate - piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate) or (simulated_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate)) and ((piece.x_coordinate - i == piece.y_coordinate - j) or (piece.x_coordinate - i == j - piece.y_coordinate)):
											potential_move = False
									elif (i > piece.x_coordinate > simulated_piece.x_coordinate):
										if ((piece.x_coordinate - simulated_piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate) or (piece.x_coordinate - simulated_piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate)) and ((i - piece.x_coordinate == j - piece.y_coordinate) or (i - piece.x_coordinate == piece.y_coordinate - j)):
											potential_move = False
								if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
					elif simulated_piece.piece == "rook":
						if ((i > simulated_piece.x_coordinate or i < simulated_piece.x_coordinate) and j == simulated_piece.y_coordinate) or ((j > simulated_piece.y_coordinate or j < simulated_piece.y_coordinate) and i == simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if piece.active == True:
										if j == simulated_piece.y_coordinate == piece.y_coordinate:
											if (i < piece.x_coordinate < simulated_piece.x_coordinate) or (i > piece.x_coordinate > simulated_piece.x_coordinate):
												potential_move = False
										elif i == simulated_piece.x_coordinate == piece.x_coordinate:
											if (j < piece.y_coordinate < simulated_piece.y_coordinate) or (j > piece.y_coordinate > simulated_piece.y_coordinate):
												potential_move = False
										if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
											potential_move = False
					elif simulated_piece.piece == "queen":
						if ((i > simulated_piece.x_coordinate or i < simulated_piece.x_coordinate) and j == simulated_piece.y_coordinate) or ((j > simulated_piece.y_coordinate or j < simulated_piece.y_coordinate) and i == simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece != simulated_piece:
									if piece.active == True:
										if j == simulated_piece.y_coordinate == piece.y_coordinate:
											if (i < piece.x_coordinate < simulated_piece.x_coordinate) or (i > piece.x_coordinate > simulated_piece.x_coordinate):
												potential_move = False
										elif i == simulated_piece.x_coordinate == piece.x_coordinate:
											if (j < piece.y_coordinate < simulated_piece.y_coordinate) or (j > piece.y_coordinate > simulated_piece.y_coordinate):
												potential_move = False
										if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
											potential_move = False
						elif (simulated_piece.x_coordinate - i == simulated_piece.y_coordinate - j or simulated_piece.x_coordinate - i == j - simulated_piece.y_coordinate or simulated_piece.y_coordinate - j == simulated_piece.x_coordinate - i or simulated_piece.y_coordinate - j == i - simulated_piece.x_coordinate):
							potential_move = True
							for piece in Piece.piece_list:
								if piece.active == True:
									if (i < piece.x_coordinate < simulated_piece.x_coordinate):
										if ((simulated_piece.x_coordinate - piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate) or (simulated_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate)) and ((piece.x_coordinate - i == piece.y_coordinate - j) or (piece.x_coordinate - i == j - piece.y_coordinate)):
											potential_move = False
									elif (i > piece.x_coordinate > simulated_piece.x_coordinate):
										if ((piece.x_coordinate - simulated_piece.x_coordinate == piece.y_coordinate - simulated_piece.y_coordinate) or (piece.x_coordinate - simulated_piece.x_coordinate == simulated_piece.y_coordinate - piece.y_coordinate)) and ((i - piece.x_coordinate == j - piece.y_coordinate) or (i - piece.x_coordinate == piece.y_coordinate - j)):
											potential_move = False
								if piece.colour == "black" and i == piece.x_coordinate and j == piece.y_coordinate:
									potential_move = False
				if potential_move == True:
					simulated_piece.potential_move.append((i,j))

# def aiMove():
	#take the potential moves of all pieces
	#determine best move based on pieve value
	#calculate cost function for piece in danger by running potential moves for other player

def initializeBoard():
	global current_turn
	global image_size
	global bpawn_list
	global wpawn_list
	global wking_list
	global bking_list
	global wrook
	global brook
	global wqueen
	global bqueen
	global wbishop
	global bbishop
	global wknight
	global bknight

	current_turn = 0
	image_size = (squareSize, squareSize)
	bpawn_list = {}
	bpawn = pygame.image.load('bpawn.png')
	bpawn = pygame.transform.scale(bpawn, image_size)
	brook_list = {}
	brook = pygame.image.load('brook.png')
	brook = pygame.transform.scale(brook, image_size)
	bknight_list = {}
	bknight = pygame.image.load('bknight.png')
	bknight = pygame.transform.scale(bknight, image_size)
	bbishop_list = {}
	bbishop = pygame.image.load('bbishop.png')
	bbishop = pygame.transform.scale(bbishop, image_size)
	bqueen_list = {}
	bqueen = pygame.image.load('bqueen.png')
	bqueen = pygame.transform.scale(bqueen, image_size)
	bking_list = {}
	bking = pygame.image.load('bking.png')
	bking = pygame.transform.scale(bking, image_size)

	wpawn_list = {}
	wpawn = pygame.image.load('wpawn.png')
	wpawn = pygame.transform.scale(wpawn, image_size)
	wrook_list = {}
	wrook = pygame.image.load('wrook.png')
	wrook = pygame.transform.scale(wrook, image_size)
	wknight_list = {}
	wknight = pygame.image.load('wknight.png')
	wknight = pygame.transform.scale(wknight, image_size)
	wbishop_list = {}
	wbishop = pygame.image.load('wbishop.png')
	wbishop = pygame.transform.scale(wbishop, image_size)
	wqueen_list = {}
	wqueen = pygame.image.load('wqueen.png')
	wqueen = pygame.transform.scale(wqueen, image_size)
	wking_list = {}
	wking = pygame.image.load('wking.png')
	wking = pygame.transform.scale(wking, image_size)

	for i in range(0, 8):
		bpawn_list[i] = Piece(bpawn, "bpawn", "black", "pawn", int(i), 1, x_coordinates[i], y_coordinates[1], True, 1, False, x_coordinates[i], y_coordinates[1], 1)
		wpawn_list[i] = Piece(wpawn, "wpawn", "white", "pawn", int(i), 6, x_coordinates[i], y_coordinates[6], True, 1, False, x_coordinates[i], y_coordinates[6], 1)
	for i in range (0, 8, 7):
		brook_list[i] = Piece(brook, "brook", "black", "rook", int(i), 0, x_coordinates[i], y_coordinates[0], True, 1, False, x_coordinates[i], y_coordinates[0], 5)
		wrook_list[i] = Piece(wrook, "wrook", "white", "rook", int(i), 7, x_coordinates[i], y_coordinates[7], True, 1, False, x_coordinates[i], y_coordinates[7], 5)
	for i in range(1, 8, 5):
		bknight_list[i] = Piece(bknight, "bknight", "black", "knight", int(i), 0, x_coordinates[i], y_coordinates[0], True, 0, False, x_coordinates[i], y_coordinates[0], 3)
		wknight_list[i] = Piece(wknight, "wknight", "white", "knight", int(i), 7, x_coordinates[i], y_coordinates[7], True, 0, False, x_coordinates[i], y_coordinates[7], 3)
	for i in range(2, 8, 3):
		bbishop_list[i] = Piece(bbishop, "bbishop", "black", "bishop", int(i), 0, x_coordinates[i], y_coordinates[0], True, 0, False, x_coordinates[i], y_coordinates[0], 3)
		wbishop_list[i] = Piece(wbishop, "wbishop", "white", "bishop", int(i), 7, x_coordinates[i], y_coordinates[7], True, 0, False, x_coordinates[i], y_coordinates[7], 3)
	bqueen_list[0] = Piece(bqueen, "bqueen", "black", "queen", 3, 0, x_coordinates[3], y_coordinates[0], True, 0, False, x_coordinates[3], y_coordinates[0], 9)
	wqueen_list[0] = Piece(wqueen, "wqueen", "white", "queen", 3, 7, x_coordinates[3], y_coordinates[7], True, 0, False, x_coordinates[3], y_coordinates[7], 9)
	bking_list[0] = Piece(bking, "bking", "black", "king", 4, 0, x_coordinates[4], y_coordinates[0], True, 1, False, x_coordinates[4], y_coordinates[0], 10)
	wking_list[0] = Piece(wking, "wking", "white", "king", 4, 7, x_coordinates[4], y_coordinates[7], True, 1, False, x_coordinates[4], y_coordinates[7], 10)

	for piece in Piece.piece_list:
		test = potentialMoves(piece)

def displayPieces():
	for piece in Piece.piece_list:
		if piece.active == True:
			if piece != selected_piece:
				screen.blit(piece.image, (piece.x_position, piece.y_position))
	if selected_piece != None:
		screen.blit(selected_piece.image, (selected_piece.x_position, selected_piece.y_position))

def resizePieces():
	global squareSize
	for piece in Piece.piece_list:
		piece.image = pygame.image.load(f'{piece.name}.png')
		piece.image = pygame.transform.scale(piece.image, (squareSize, squareSize))
		piece.x_position = x_coordinates[piece.x_coordinate]
		piece.y_position = y_coordinates[piece.y_coordinate]

def mouseControl():
	global current_square
	global current_coordinate
	global selected_piece
	global bpawn_promotion
	global wpawn_promotion

	colour = (156, 123, 94)
	black_or_white = black

	x, y = pygame.mouse.get_pos()
	for i in range(0, 8):
		if (x_coordinates[int(i)] <= x <= x_coordinates[int(i)] + squareSize):
			for j in range(0, 8):
				if (y_coordinates[j] <= y <= (y_coordinates[j] + squareSize)):
					surface = pygame.Surface((squareSize + 0.01 * squareSize, squareSize + 0.01 * squareSize))
					surface.set_alpha(128)
					surface.fill((30,144,255))
					screen.blit(surface, (x_coordinates[i], y_coordinates[j]))
					# pygame.draw.rect(screen, colour, [x_coordinates[i], y_coordinates[j], squareSize + 0.01 * squareSize, squareSize + 0.01 * squareSize])
					current_square = (x_coordinates[i], y_coordinates[j])
					current_coordinate = (i, j)
					if selected_piece != None:
						for position in selected_piece.potential_move:
							# pygame.draw.rect(screen, colour, [x_coordinates[position[0]], y_coordinates[position[1]], squareSize + 0.01 * squareSize, squareSize + 0.01 * squareSize])
							screen.blit(surface, [x_coordinates[position[0]], y_coordinates[position[1]]])

	for i in range(0, 4):
		if bpawn_promotion != None:
			if (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize) <= x <= (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize) + squareSize)) and (y_coordinates[7] + (1.5 * squareSize) <= y <= y_coordinates[7] + (1.5 * squareSize) + squareSize):
				pygame.draw.rect(screen, colour, [x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize),  (y_coordinates[7] + (1.5 * squareSize)), squareSize, squareSize])
				if i == 0:
					screen.blit(bqueen, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
				elif i == 1:
					screen.blit(brook, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
				elif i == 2:
					screen.blit(bbishop, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
				elif i == 3:
					screen.blit(bknight, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
		if wpawn_promotion != None:
			if (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize) <= x <= x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize) + squareSize) and (y_coordinates[0] - (1.5 * squareSize) - 0.02 * squareSize <= y <= y_coordinates[0] - (1.5 * squareSize) - 0.02 * squareSize + squareSize):
				pygame.draw.rect(screen, colour, [x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize)), squareSize, squareSize])
				if i == 0:
					screen.blit(wqueen, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
				elif i == 1:
					screen.blit(wrook, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
				elif i == 2:
					screen.blit(wbishop, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
				elif i == 3:
					screen.blit(wknight, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))

def Check():
	global white_check
	global black_check
	white_check = False
	black_check = False
	for piece in Piece.piece_list:
		if piece.active == True:
			if piece.colour == "white":
				for move in piece.potential_move:
					if move[0] == bking_list[0].x_coordinate and move[1] == bking_list[0].y_coordinate:
						black_check = True
						print("Black is in check")
			elif piece.colour == "black":
				for move in piece.potential_move:
					if move[0] == wking_list[0].x_coordinate and move[1] == wking_list[0].y_coordinate:
						white_check = True
						print("White is in check")


def promotion():
	global bpawn_list
	global wpawn_list
	global bpawn_promotion
	global wpawn_promotion

	for piece in Piece.piece_list:
		if piece.piece == "pawn":
			if piece.y_coordinate == 7:
				bpawn_promotion = piece.x_coordinate
			elif piece.y_coordinate == 0:
				wpawn_promotion = piece.x_coordinate

def displayPromotion():
	global bpawn_list
	global wpawn_list
	global bpawn_promotion
	global wpawn_promotion
	global x_coordinates
	global y_coordinates
	global squareSize
	global wrook
	global brook
	global wqueen
	global bqueen
	global wbishop
	global bbishop
	global wknight
	global bknight

	if bpawn_promotion != None:
		grid_pattern = 1
		pygame.draw.rect(screen, black, [x_coordinates[bpawn_promotion] - (2 * squareSize) - 0.02 * squareSize, y_coordinates[7] + (1.5 * squareSize) - 0.02 * squareSize, (4 * squareSize) + 0.04 * squareSize, squareSize + 0.04 * squareSize])
		for i in range(0, 4):
			if grid_pattern % 2:
				colour = (white)
			else:
				colour = (black)
			pygame.draw.rect(screen, colour, [x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize)), squareSize, squareSize])
			grid_pattern = grid_pattern + 1
			if i == 0:
				screen.blit(bqueen, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
			elif i == 1:
				screen.blit(brook, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
			elif i == 2:
				screen.blit(bbishop, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
			elif i == 3:
				screen.blit(bknight, (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize), (y_coordinates[7] + (1.5 * squareSize))))
	if wpawn_promotion != None:
		grid_pattern = 1
		pygame.draw.rect(screen, black, [x_coordinates[wpawn_promotion] - (2 * squareSize) - 0.02 * squareSize, y_coordinates[0] - (1.5 * squareSize) - 0.02 * squareSize, (4 * squareSize) + 0.04 * squareSize, squareSize + 0.04 * squareSize])
		for i in range(0, 4):
			if grid_pattern % 2:
				colour = (white)
			else:
				colour = (black)
			pygame.draw.rect(screen, colour, [x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize)), squareSize, squareSize])
			grid_pattern = grid_pattern + 1
			if i == 0:
				screen.blit(wqueen, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
			elif i == 1:
				screen.blit(wrook, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
			elif i == 2:
				screen.blit(wbishop, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))
			elif i == 3:
				screen.blit(wknight, (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize), (y_coordinates[0] - (1.5 * squareSize))))


def legalMove():
	global legal_move
	global current_turn
	legal_move = False
	if selected_piece != None:
		if current_turn == 0:
			if selected_piece.colour == "white":
				if selected_piece.piece == "pawn":
					if (current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate - 1) or (selected_piece.unique_move == 1 and current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate - 2):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
									legal_move = False
					for piece in Piece.piece_list:
						if piece != selected_piece:
							if (current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and current_coordinate[1] == selected_piece.y_coordinate - 1 and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = True
								if piece.colour == "white":
									legal_move = False
							elif piece.en_passant == True and (current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and current_coordinate[1] == selected_piece.y_coordinate - 1 and (selected_piece.x_coordinate + 1 == piece.x_coordinate or selected_piece.x_coordinate - 1 == piece.x_coordinate) and selected_piece.y_coordinate == piece.y_coordinate and current_coordinate[0] == piece.x_coordinate:
								legal_move = True
								if piece.colour == "white":
									legal_move = False	
								else:
									piece.active = False	
					if legal_move == True:
						for piece in Piece.piece_list:
							piece.en_passant = False
						if selected_piece.unique_move == 1 and current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate - 2:
							selected_piece.en_passant = True
						selected_piece.unique_move = 0
						current_turn = 1
				elif selected_piece.piece == "knight":
					if ((current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and (current_coordinate[1] == selected_piece.y_coordinate + 2 or current_coordinate[1] == selected_piece.y_coordinate - 2) or (current_coordinate[0] == selected_piece.x_coordinate + 2 or current_coordinate[0] == selected_piece.x_coordinate - 2) and (current_coordinate[1] == selected_piece.y_coordinate + 1 or current_coordinate[1] == selected_piece.y_coordinate - 1)):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False
				elif selected_piece.piece == "king":
					if (-1 <= current_coordinate[0] - selected_piece.x_coordinate <= 1) and (-1 <= current_coordinate[1] - selected_piece.y_coordinate <= 1):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False
					elif selected_piece.unique_move == 1:
						if ((selected_piece.x_coordinate + 2 == current_coordinate[0]) and selected_piece.y_coordinate == current_coordinate[1] and Piece.piece_list[19].unique_move == 1):
							legal_move = True
							for piece in Piece.piece_list:
								if piece != selected_piece:
									if (piece.y_coordinate == selected_piece.y_coordinate) and (selected_piece.x_coordinate <= piece.x_coordinate <= current_coordinate[0]):
										legal_move = False
									if piece.colour == "black":
										for move in piece.potential_move:
											if (move[1] == selected_piece.y_coordinate and (move[0] == 4 or move[0] == 5 or move[0] == 6)):
												print("line 600")
												legal_move == False


							if legal_move == True:
								Piece.piece_list[19].x_coordinate = 5
								Piece.piece_list[19].x_position = x_coordinates[5]
								Piece.piece_list[19].unique_move = 0
						elif (selected_piece.x_coordinate - 2 == current_coordinate[0]) and selected_piece.y_coordinate == current_coordinate[1] and Piece.piece_list[17].unique_move == 1:
							legal_move = True
							for piece in Piece.piece_list:
								if piece != selected_piece:
									if (piece.y_coordinate == selected_piece.y_coordinate) and (selected_piece.x_coordinate >= piece.x_coordinate >= current_coordinate[0]):
										legal_move = False
							if legal_move == True:
								Piece.piece_list[17].x_coordinate = 3
								Piece.piece_list[17].x_position = x_coordinates[3]
								Piece.piece_list[17].unique_move = 0
					if legal_move == True:
						selected_piece.unique_move = 0
				elif selected_piece.piece == "bishop":
					if (selected_piece.x_coordinate - current_coordinate[0] == selected_piece.y_coordinate - current_coordinate[1] or selected_piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - selected_piece.y_coordinate or selected_piece.y_coordinate - current_coordinate[1] == selected_piece.x_coordinate - current_coordinate[0] or selected_piece.y_coordinate - current_coordinate[1] == current_coordinate[0] - selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.active == True:
								if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate):
									if ((selected_piece.x_coordinate - piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate) or (selected_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate)) and ((piece.x_coordinate - current_coordinate[0] == piece.y_coordinate - current_coordinate[1]) or (piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - piece.y_coordinate)):
										legal_move = False
								elif (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
									if ((piece.x_coordinate - selected_piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate) or (piece.x_coordinate - selected_piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate)) and ((current_coordinate[0] - piece.x_coordinate == current_coordinate[1] - piece.y_coordinate) or (current_coordinate[0] - piece.x_coordinate == piece.y_coordinate - current_coordinate[1])):
										legal_move = False
							if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False
				elif selected_piece.piece == "rook":
					if ((current_coordinate[0] > selected_piece.x_coordinate or current_coordinate[0] < selected_piece.x_coordinate) and current_coordinate[1] == selected_piece.y_coordinate) or ((current_coordinate[1] > selected_piece.y_coordinate or current_coordinate[1] < selected_piece.y_coordinate) and current_coordinate[0] == selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if piece.active == True:
									if current_coordinate[1] == selected_piece.y_coordinate == piece.y_coordinate:
										if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate) or (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
											legal_move = False
									elif current_coordinate[0] == selected_piece.x_coordinate == piece.x_coordinate:
										if (current_coordinate[1] < piece.y_coordinate < selected_piece.y_coordinate) or (current_coordinate[1] > piece.y_coordinate > selected_piece.y_coordinate):
											legal_move = False
									if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
										legal_move = False
					if legal_move == True:
						selected_piece.unique_move = 0
				elif selected_piece.piece == "queen":
					if ((current_coordinate[0] > selected_piece.x_coordinate or current_coordinate[0] < selected_piece.x_coordinate) and current_coordinate[1] == selected_piece.y_coordinate) or ((current_coordinate[1] > selected_piece.y_coordinate or current_coordinate[1] < selected_piece.y_coordinate) and current_coordinate[0] == selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if piece.active == True:
									if current_coordinate[1] == selected_piece.y_coordinate == piece.y_coordinate:
										if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate) or (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
											legal_move = False
									elif current_coordinate[0] == selected_piece.x_coordinate == piece.x_coordinate:
										if (current_coordinate[1] < piece.y_coordinate < selected_piece.y_coordinate) or (current_coordinate[1] > piece.y_coordinate > selected_piece.y_coordinate):
											legal_move = False
									if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
										legal_move = False
					elif (selected_piece.x_coordinate - current_coordinate[0] == selected_piece.y_coordinate - current_coordinate[1] or selected_piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - selected_piece.y_coordinate or selected_piece.y_coordinate - current_coordinate[1] == selected_piece.x_coordinate - current_coordinate[0] or selected_piece.y_coordinate - current_coordinate[1] == current_coordinate[0] - selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.active == True:
								if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate):
									if ((selected_piece.x_coordinate - piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate) or (selected_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate)) and ((piece.x_coordinate - current_coordinate[0] == piece.y_coordinate - current_coordinate[1]) or (piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - piece.y_coordinate)):
										legal_move = False
								elif (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
									if ((piece.x_coordinate - selected_piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate) or (piece.x_coordinate - selected_piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate)) and ((current_coordinate[0] - piece.x_coordinate == current_coordinate[1] - piece.y_coordinate) or (current_coordinate[0] - piece.x_coordinate == piece.y_coordinate - current_coordinate[1])):
										legal_move = False
							if piece.colour == "white" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False

				if legal_move == True:
					current_turn = 1

		elif current_turn == 1:
			if selected_piece.colour == "black":
				if selected_piece.piece == "pawn":
					if (current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate + 1) or (selected_piece.unique_move == 1 and current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate + 2):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
									legal_move = False
					for piece in Piece.piece_list:
						if piece != selected_piece:
							if (current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and current_coordinate[1] == selected_piece.y_coordinate + 1 and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = True
								if piece.colour == "black":
									legal_move = False
							elif piece.en_passant == True and (current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and current_coordinate[1] == selected_piece.y_coordinate + 1 and (selected_piece.x_coordinate + 1 == piece.x_coordinate or selected_piece.x_coordinate - 1 == piece.x_coordinate) and selected_piece.y_coordinate == piece.y_coordinate and current_coordinate[0] == piece.x_coordinate:
								legal_move = True
								if piece.colour == "black":
									legal_move = False	
								else:
									piece.active = False
					if legal_move == True:
						for piece in Piece.piece_list:
							piece.en_passant = False
						if selected_piece.unique_move == 1 and current_coordinate[0] == selected_piece.x_coordinate and current_coordinate[1] == selected_piece.y_coordinate + 2:
							selected_piece.en_passant = True
						selected_piece.unique_move = 0
						current_turn = 0
				elif selected_piece.piece == "knight":
					if ((current_coordinate[0] == selected_piece.x_coordinate + 1 or current_coordinate[0] == selected_piece.x_coordinate - 1) and (current_coordinate[1] == selected_piece.y_coordinate + 2 or current_coordinate[1] == selected_piece.y_coordinate - 2) or (current_coordinate[0] == selected_piece.x_coordinate + 2 or current_coordinate[0] == selected_piece.x_coordinate - 2) and (current_coordinate[1] == selected_piece.y_coordinate + 1 or current_coordinate[1] == selected_piece.y_coordinate - 1)):
						for piece in Piece.piece_list:
							legal_move = True
							if piece.colour == "black":
								legal_move = False
				elif selected_piece.piece == "king":
					if (-1 <= current_coordinate[0] - selected_piece.x_coordinate <= 1) and (-1 <= current_coordinate[1] - selected_piece.y_coordinate <= 1):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.colour == "black" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False
					elif selected_piece.unique_move == 1:
						if ((selected_piece.x_coordinate + 2 == current_coordinate[0]) and selected_piece.y_coordinate == current_coordinate[1] and Piece.piece_list[18].unique_move == 1):
							legal_move = True
							for piece in Piece.piece_list:
								if piece != selected_piece:
									if (piece.y_coordinate == selected_piece.y_coordinate) and (selected_piece.x_coordinate <= piece.x_coordinate <= current_coordinate[0]):
										legal_move = False
							if legal_move == True:
								Piece.piece_list[18].x_coordinate = 5
								Piece.piece_list[18].x_position = x_coordinates[5]
								Piece.piece_list[18].unique_move = 0
						elif (selected_piece.x_coordinate - 2 == current_coordinate[0]) and selected_piece.y_coordinate == current_coordinate[1] and Piece.piece_list[16].unique_move == 1:
							legal_move = True
							for piece in Piece.piece_list:
								if piece != selected_piece:
									if (piece.y_coordinate == selected_piece.y_coordinate) and (selected_piece.x_coordinate >= piece.x_coordinate >= current_coordinate[0]):
										legal_move = False
							if legal_move == True:
								Piece.piece_list[16].x_coordinate = 3
								Piece.piece_list[16].x_position = x_coordinates[3]
								Piece.piece_list[16].unique_move = 0
					if legal_move == True:
						selected_piece.unique_move = 0
				elif selected_piece.piece == "bishop":
					if (selected_piece.x_coordinate - current_coordinate[0] == selected_piece.y_coordinate - current_coordinate[1] or selected_piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - selected_piece.y_coordinate or selected_piece.y_coordinate - current_coordinate[1] == selected_piece.x_coordinate - current_coordinate[0] or selected_piece.y_coordinate - current_coordinate[1] == current_coordinate[0] - selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.active == True:
								if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate):
									if ((selected_piece.x_coordinate - piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate) or (selected_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate)) and ((piece.x_coordinate - current_coordinate[0] == piece.y_coordinate - current_coordinate[1]) or (piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - piece.y_coordinate)):
										legal_move = False
								elif (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
									if ((piece.x_coordinate - selected_piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate) or (piece.x_coordinate - selected_piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate)) and ((current_coordinate[0] - piece.x_coordinate == current_coordinate[1] - piece.y_coordinate) or (current_coordinate[0] - piece.x_coordinate == piece.y_coordinate - current_coordinate[1])):
										legal_move = False
							if piece.colour == "black" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False
				elif selected_piece.piece == "rook":
					if ((current_coordinate[0] > selected_piece.x_coordinate or current_coordinate[0] < selected_piece.x_coordinate) and current_coordinate[1] == selected_piece.y_coordinate) or ((current_coordinate[1] > selected_piece.y_coordinate or current_coordinate[1] < selected_piece.y_coordinate) and current_coordinate[0] == selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if piece.active == True:
									if current_coordinate[1] == selected_piece.y_coordinate == piece.y_coordinate:
										if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate) or (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
											legal_move = False
									elif current_coordinate[0] == selected_piece.x_coordinate == piece.x_coordinate:
										if (current_coordinate[1] < piece.y_coordinate < selected_piece.y_coordinate) or (current_coordinate[1] > piece.y_coordinate > selected_piece.y_coordinate):
											legal_move = False
									if piece.colour == "black" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
										legal_move = False
						if legal_move == True:
							selected_piece.unique_move = 0
				elif selected_piece.piece == "queen":
					if ((current_coordinate[0] > selected_piece.x_coordinate or current_coordinate[0] < selected_piece.x_coordinate) and current_coordinate[1] == selected_piece.y_coordinate) or ((current_coordinate[1] > selected_piece.y_coordinate or current_coordinate[1] < selected_piece.y_coordinate) and current_coordinate[0] == selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece != selected_piece:
								if piece.active == True:
									if current_coordinate[1] == selected_piece.y_coordinate == piece.y_coordinate:
										if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate) or (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
											legal_move = False
									elif current_coordinate[0] == selected_piece.x_coordinate == piece.x_coordinate:
										if (current_coordinate[1] < piece.y_coordinate < selected_piece.y_coordinate) or (current_coordinate[1] > piece.y_coordinate > selected_piece.y_coordinate):
											legal_move = False
									if piece.colour == "black" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
										legal_move = False
					elif (selected_piece.x_coordinate - current_coordinate[0] == selected_piece.y_coordinate - current_coordinate[1] or selected_piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - selected_piece.y_coordinate or selected_piece.y_coordinate - current_coordinate[1] == selected_piece.x_coordinate - current_coordinate[0] or selected_piece.y_coordinate - current_coordinate[1] == current_coordinate[0] - selected_piece.x_coordinate):
						legal_move = True
						for piece in Piece.piece_list:
							if piece.active == True:
								if (current_coordinate[0] < piece.x_coordinate < selected_piece.x_coordinate):
									if ((selected_piece.x_coordinate - piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate) or (selected_piece.x_coordinate - piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate)) and ((piece.x_coordinate - current_coordinate[0] == piece.y_coordinate - current_coordinate[1]) or (piece.x_coordinate - current_coordinate[0] == current_coordinate[1] - piece.y_coordinate)):
										legal_move = False
								elif (current_coordinate[0] > piece.x_coordinate > selected_piece.x_coordinate):
									if ((piece.x_coordinate - selected_piece.x_coordinate == piece.y_coordinate - selected_piece.y_coordinate) or (piece.x_coordinate - selected_piece.x_coordinate == selected_piece.y_coordinate - piece.y_coordinate)) and ((current_coordinate[0] - piece.x_coordinate == current_coordinate[1] - piece.y_coordinate) or (current_coordinate[0] - piece.x_coordinate == piece.y_coordinate - current_coordinate[1])):
										legal_move = False
							if piece.colour == "black" and current_coordinate[0] == piece.x_coordinate and current_coordinate[1] == piece.y_coordinate:
								legal_move = False

				if legal_move == True:
					current_turn = 0
	if current_turn == 0:
		print("White's turn")
	elif current_turn == 1:
		print("Black's turn")


def main():
	global selected_piece
	global current_coordinate
	global current_turn
	global white_check
	global black_check
	global bpawn_promotion
	global wpawn_promotion

	piece_memory = None
	running = True
	drawGrid()
	initializeBoard()
	while running:
		screen.fill(white)
		drawGrid()
		displayPromotion()
		mouseControl()
		displayPieces()
		pygame.event.pump()
		for event in pygame.event.get():
			if (event.type == MOUSEBUTTONDOWN and selected_piece == None):
				for piece in Piece.piece_list:
					if current_coordinate != None:
						if (piece.x_coordinate, piece.y_coordinate) == current_coordinate:
							selected_piece = piece
							x, y = pygame.mouse.get_pos()
							displacement_x = (x - selected_piece.x_position)
							displacement_y = (y - selected_piece.y_position)

			if (event.type == MOUSEBUTTONUP and selected_piece != None):
				legalMove()
				if legal_move == True:
					memory_x_coordinate = selected_piece.x_coordinate
					selected_piece.x_coordinate = current_coordinate[0]
					selected_piece.x_position = x_coordinates[selected_piece.x_coordinate]
					memory_y_coordinate = selected_piece.y_coordinate
					selected_piece.y_coordinate = current_coordinate[1]
					selected_piece.y_position = y_coordinates[selected_piece.y_coordinate]
					for piece in Piece.piece_list:
						if piece.x_coordinate == selected_piece.x_coordinate and piece.y_coordinate == selected_piece.y_coordinate and selected_piece != piece:
							piece_memory = piece
							piece.active = False
							piece_memory_x_p = piece.x_position
							piece.x_position = None
							piece_memory_y_p = piece.y_position
							piece.y_position = None
							piece_memory_x_c = piece.x_coordinate
							piece.x_coordinate = None
							piece_memory_y_c = piece.y_coordinate
							piece.y_coordinate = None
						piece.potential_move.clear()
						potentialMoves(piece)
					Check()
					if (selected_piece.colour == "white" and white_check == True) or (selected_piece.colour == "black" and black_check == True):
						if current_turn == 0:
							current_turn = 1
						elif current_turn == 1:
							current_turn = 0
						selected_piece.x_coordinate = memory_x_coordinate
						selected_piece.x_position = x_coordinates[memory_x_coordinate]
						selected_piece.y_coordinate = memory_y_coordinate
						selected_piece.y_position = y_coordinates[memory_y_coordinate]

						if piece_memory != None:
							piece_memory.active = True
							piece_memory.x_position = piece_memory_x_p
							piece_memory.y_position = piece_memory_y_p
							piece_memory.x_coordinate = piece_memory_x_c
							piece_memory.y_coordinate = piece_memory_y_c

						legal_move == False

						for piece in Piece.piece_list:
							piece.potential_move.clear()
							potentialMoves(piece)
					promotion()
					selected_piece = None
				elif legal_move == False:
					selected_piece.x_position = x_coordinates[selected_piece.x_coordinate]
					selected_piece.y_position = y_coordinates[selected_piece.y_coordinate]
					selected_piece = None
			if event.type == MOUSEBUTTONUP:
				x, y = pygame.mouse.get_pos()
				for i in range(0, 4):
					if bpawn_promotion != None:
						if (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize) <= x <= (x_coordinates[i] - (2 * squareSize) + (bpawn_promotion * squareSize) + squareSize)) and (y_coordinates[7] + (1.5 * squareSize) <= y <= y_coordinates[7] + (1.5 * squareSize) + squareSize):
							if i == 0:
								for piece in Piece.piece_list:
									if piece.x_coordinate == bpawn_promotion and piece.y_coordinate == 7 and piece.piece == "pawn":
										piece.image = bqueen
										piece.name = "bqueen"
										piece.piece = "queen"
							elif i == 1:
								for piece in Piece.piece_list:
									if piece.x_coordinate == bpawn_promotion and piece.y_coordinate == 7 and piece.piece == "pawn":
										piece.image = brook
										piece.name = "brook"
										piece.piece = "rook"
							elif i == 2:
								for piece in Piece.piece_list:
									if piece.x_coordinate == bpawn_promotion and piece.y_coordinate == 7 and piece.piece == "pawn":
										piece.image = bbishop
										piece.name = "bbishop"
										piece.piece = "bishop"
							elif i == 3:
								for piece in Piece.piece_list:
									if piece.x_coordinate == bpawn_promotion and piece.y_coordinate == 7 and piece.piece == "pawn":
										piece.image = bknight
										piece.name = "bknight"
										piece.piece = "knight"
							bpawn_promotion = None
					if wpawn_promotion != None:
						if (x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize) <= x <= x_coordinates[i] - (2 * squareSize) + (wpawn_promotion * squareSize) + squareSize) and (y_coordinates[0] - (1.5 * squareSize) - 0.02 * squareSize <= y <= y_coordinates[0] - (1.5 * squareSize) - 0.02 * squareSize + squareSize):
							if i == 0:
								for piece in Piece.piece_list:
									if piece.x_coordinate == wpawn_promotion and piece.y_coordinate == 0 and piece.piece == "pawn":
										piece.image = wqueen
										piece.name = "wqueen"
										piece.piece = "queen"
							elif i == 1:
								for piece in Piece.piece_list:
									if piece.x_coordinate == wpawn_promotion and piece.y_coordinate == 0 and piece.piece == "pawn":
										piece.image = wrook
										piece.name = "wrook"
										piece.piece = "rook"
							elif i == 2:
								for piece in Piece.piece_list:
									if piece.x_coordinate == wpawn_promotion and piece.y_coordinate == 0 and piece.piece == "pawn":
										piece.image = wbishop
										piece.name = "wbishop"
										piece.piece = "bishop"
							elif i == 3:
								for piece in Piece.piece_list:
									if piece.x_coordinate == wpawn_promotion and piece.y_coordinate == 0 and piece.piece == "pawn":
										piece.image = wknight
										piece.name = "wknight"
										piece.piece = "knight"
							wpawn_promotion = None

			if event.type == QUIT:
				running = False
			elif event.type == VIDEORESIZE:
				screen.fill(white)
				drawGrid()
				resizePieces()
				continue
			elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
				screen.fill(white)
				drawGrid()
				resizePieces()
				continue
		x, y = pygame.mouse.get_pos()
		if selected_piece != None:
			selected_piece.x_position = x - displacement_x
			selected_piece.y_position = y - displacement_y

		pygame.display.update()
		pygame.display.flip()
if __name__ == '__main__':
	main()