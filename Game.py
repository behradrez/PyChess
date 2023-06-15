import pygame
import sys

import Board
import Piece

pygame.init()
screen = pygame.display.set_mode((500, 500))
board = Board.Board()
board.update_valid_moves()

square_is_selected = False
selected_square = None
valid_squares = []
castle = []

checking_squares = None
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            print("qqqqq")

    screen.fill("Brown")
    board.draw_board(screen)
    if not board.is_game_over():
        pygame.display.update()
    else:
        print("Game over " + board.turn + " checkmated")

    board.update_valid_moves()

    for square in board.squares:
        if square.piece.type == 'King':
            if square.piece.piece_color == board.turn and board.checked:
                square.color = 'Pink'
            else:
                square.color = square.original_color

        if square.check_click():
            if (not square_is_selected or selected_square.piece.piece_color == square.piece.piece_color) \
                    and square.piece.piece_color == board.turn:
                square_is_selected = True
                selected_square = square
                print(selected_square)

                square.color = 'Blue'
                if square.piece.type == 'King':
                    castle = board.is_castling_possible(square.piece.piece_color)
                valid_squares = square.display_valid_moves()

            elif square_is_selected:
                for i in range(len(castle)):
                    if square == castle[i][1]:
                        board.move_piece(selected_square, square, True)
                        board.move_piece(castle[i][2], castle[i][3])

                if square in valid_squares:
                    if square.has_piece():
                        square.piece = Piece.Piece("None", "None")
                    board.move_piece(selected_square, square)
                    board.update_valid_moves()
                    if board.checked:
                        checking_squares = valid_squares

                    print(' to  ' + square.column_letter + str(square.row))
                square_is_selected = False
                selected_square = None

            while board.state == 'PROMOTE':
                print("Press key to promote pawn: Q/B/H/R")
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_h:
                            square.piece.promote('Horse')
                            board.state = None

                        elif event.key == pygame.K_q:
                            square.piece.promote("Queen")
                            board.state = None

                        elif event.key == pygame.K_b:
                            square.piece.promote("Bishop")
                            board.state = None

                        elif event.key == pygame.K_r:
                            square.piece.promote("Rook")
                            board.state = None
