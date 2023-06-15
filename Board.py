import pygame, sys

import BoardSquare
from BoardSquare import ChessSquare
from Piece import Piece
import time


class Board:
    def __init__(self):
        # All chess squares on the board
        self.squares = []

        # Determining whose turn it is
        self.num_moves = 0
        self.turn = 'White'

        # Info needed to deal with checks & checkmate
        self.checked = False
        self.list_of_checking_trajectories = []

        # Game State for edge-situations
        self.state = None

        # List of squares containing pieces protected by other pieces
        self.protected_squares_white = []
        self.protected_squares_black = []

        # Initializing starting positions
        for j in range(1, 9):
            for i in range(1, 9):
                color = "White"
                if i > 4:
                    color = 'Black'
                square = ChessSquare(i, j)
                if i == 2:
                    square.piece = Piece("Pawn", "White")
                elif i == 7:
                    square.piece = Piece("Pawn", "Black")
                elif i == 1 or i == 8:
                    if j == 1 or j == 8:
                        square.piece = Piece("Rook", color)
                    elif j == 2 or j == 7:
                        square.piece = Piece("Horse", color)
                    elif j == 3 or j == 6:
                        square.piece = Piece("Bishop", color)
                    elif j == 4:
                        square.piece = Piece("Queen", color)
                    elif j == 5:
                        square.piece = Piece("King", color)
                self.squares.append(square)

    def draw_board(self, surface):
        # Drawing each square onto the board. Function will be called in a loop
        for square in self.squares:
            square.draw_square(surface)
            if square.has_piece():
                image = square.piece.load_pic().convert_alpha(surface)
                surface.blit(image, (square.column * 50 - 5, square.row * 50 - 5))

    def update_valid_moves(self):
        # Updates each piece's valid moves upon every call
        self.checked = False
        for square in self.squares:
            square.valid_moves = self.valid_movements(square)
            if square.check_for_checks():
                self.checked = True
                square.valid_moves = self.valid_movements(square)

        # Restricting movements of pieces if a king is in check
        if self.checked:
            for square in self.squares:
                if square.piece.type != 'King':
                    for traj in self.list_of_checking_trajectories:
                        for move in square.valid_moves:
                            if move not in traj:
                                square.valid_moves.remove(move)

    def get_selected(self):
        # Detecting a click on a board square
        for square in self.squares:
            if square.check_click():
                if square.piece.piece_color == self.turn:
                    print(square.valid_moves)
                    square.color = 'Blue'
                return square

    def get_square(self, column, row):
        # Accessing a square on the board given column and row
        for spot in self.squares:
            if spot.column == column and spot.row == row:
                return spot
        return None

    def move_piece(self, start: ChessSquare, end: ChessSquare, quiet_move = False):
        # Moving a piece from a starting square to another square
        history = str(start) + " to " + str(end)
        start.piece.past_moves.append(history)
        if end.has_piece():
            end.piece = Piece("None", "None")
        end.piece = start.piece
        start.piece = Piece("None", "None")

        # Resets check information if king was previously in check.
        # So function can only be called if it is a valid movement when in check
        if self.checked:
            self.checked = False
            self.list_of_checking_trajectories = []

        # Increments number of moves in game and switches turns
        # Quiet move in case move does not count as play (testing and double move in castling)
        if not quiet_move:
            self.num_moves += 1
        if self.num_moves % 2 == 0:
            self.turn = 'White'
        else:
            self.turn = "Black"

    def valid_movements(self, start: ChessSquare):
        # Determines valid moves for a given ChessSquare. If ChessSquare has no pieces, no moves are valid
        if not start.has_piece():
            return []
        piece_type = start.piece.type
        valid_moves = []
        if piece_type == 'Pawn':
            valid_moves = self.valid_pawn_movements(start)
        elif piece_type == "Queen":
            valid_moves = self.valid_queen_movements(start)
        elif piece_type == "Rook":
            valid_moves = self.valid_rook_movements(start)
        elif piece_type == "Bishop":
            valid_moves = self.valid_bishop_movements(start)
        elif piece_type == 'King':
            valid_moves = self.valid_king_movements(start)

        elif piece_type == 'Horse':
            valid_moves = self.valid_horse_movements(start)

        return valid_moves

    def board_check_for_checks(self):
        # Checks if there is a check on the board (detects only 1)
        for sq in self.squares:
            if sq.check_for_checks():
                return True
        return False

    def valid_horse_movements(self, start):
        # Calculates valid horse movements depending on layout of board
        val = []
        # Check trajectory array is the same for all movement calculation functions. If a piece (horse in this case)
        # checks the enemy King, the squares that must be covered in order to remove the check are listed.
        # For a check caused by a horse, it can only be removed by taking the horse piece
        check_trajectory = []
        for square in self.squares:
            row_diff = abs(square.row_difference(start))
            col_diff = abs(square.column_difference(start))

            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                if square.has_piece() and square.piece.piece_color == start.piece.piece_color:
                    if square.piece.piece_color == 'White':
                        self.protected_squares_white.append(square)
                    else:
                        self.protected_squares_black.append(square)
                    continue
                val.append(square)
                if square.piece.type == 'King':
                    check_trajectory.append(start)
                    self.list_of_checking_trajectories.append(check_trajectory)

        return val

    def valid_pawn_movements(self, start):
        # Calculates valid pawn movements
        if start.row==1 or start.row ==8:
            self.state = 'PROMOTE'
            return []

        valid_squares = []
        front = None
        if start.piece.piece_color == 'White':
            front = self.get_square(start.column, start.row + 1)
            if front is not None and not front.has_piece():
                valid_squares.append(front)
                if len(start.piece.past_moves) == 0:
                    double_start = self.get_square(start.column, start.row + 2)
                    if not double_start.has_piece():
                        valid_squares.append(double_start)

        elif start.piece.piece_color == 'Black':
            front = self.get_square(start.column, start.row - 1)
            if front is not None and not front.has_piece():
                valid_squares.append(front)
                if len(start.piece.past_moves) == 0:
                    double_start = self.get_square(start.column, start.row - 2)
                    if not double_start.has_piece():
                        valid_squares.append(double_start)

        # Front diagonal of each pawn
        diag_one = self.get_square(front.column + 1, front.row)
        diag_two = self.get_square(front.column - 1, front.row)
        if diag_two is not None and diag_two.has_piece():
            if diag_two.piece.piece_color != start.piece.piece_color:
                valid_squares.append(diag_two)
            else:
                if diag_two.piece.piece_color == 'White':
                    self.protected_squares_white.append(diag_two)
                else:
                    self.protected_squares_black.append(diag_two)

        if diag_one is not None and diag_one.has_piece():
            if diag_one.piece.piece_color != start.piece.piece_color:
                valid_squares.append(diag_one)
            else:
                if diag_one.piece.piece_color == 'White':
                    self.protected_squares_white.append(diag_one)
                else:
                    self.protected_squares_black.append(diag_one)

        for square in valid_squares:
            if square.piece.type == 'King':
                self.list_of_checking_trajectories.append([start])
        return valid_squares

    def valid_rook_movements(self, start):
        # Calculates valid rook movements
        valid_movements = []
        check_trajectory = []
        trajectory_found = False

        start_index = 0
        for i in range(1, 9):
            square = self.get_square(start.column, start.row + i)
            if square is None:
                break
            elif square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if square.piece.type == 'King':
                trajectory_found = True
            if square.has_piece():
                break
        if trajectory_found and len(check_trajectory) == 0:
            check_trajectory = valid_movements[start_index:len(valid_movements) - 1]

        start_index = len(valid_movements) - 1
        for i in range(1, 9):
            square = self.get_square(start.column, start.row - i)
            if square is None:
                break
            elif square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if square.piece.type == 'King':
                trajectory_found = True
            if square.has_piece():
                break
        if trajectory_found and len(check_trajectory) == 0:
            check_trajectory = valid_movements[start_index:len(valid_movements) - 1]

        start_index = len(valid_movements) - 1
        for i in range(1, 9):
            square = self.get_square(start.column + i, start.row)
            if square is None:
                break
            elif square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if square.piece.type == 'King':
                trajectory_found = True
            if square.has_piece():
                break
        if trajectory_found and len(check_trajectory) == 0:
            check_trajectory = valid_movements[start_index:len(valid_movements) - 1]

        start_index = len(valid_movements) - 1
        for i in range(1, 9):
            square = self.get_square(start.column - i, start.row)
            if square is None:
                break
            elif square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if square.piece.type == 'King' and not trajectory_found:
                trajectory_found = True
            if square.has_piece():
                break
        if trajectory_found and len(check_trajectory) == 0:
            check_trajectory = valid_movements[start_index:len(valid_movements) - 1]

        if trajectory_found:
            check_trajectory.append(start)
            self.list_of_checking_trajectories.append(check_trajectory)

        return valid_movements

    def valid_bishop_movements(self, start):
        # Calculates valid bishop movements.
        valid_movements = []
        check_trajectory = []
        trajectory_found = False
        for i in range(1, 9):
            if start.column + i > 8 or start.row + i > 8:
                break
            square = self.get_square(start.column + i, start.row + i)
            if square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if not trajectory_found: check_trajectory.append(square)
            if square.has_piece():
                break

        for square in check_trajectory:
            if square.piece.type == 'King':
                trajectory_found = True
        if not trajectory_found:
            check_trajectory.clear()

        for i in range(1, 9):
            if start.column - i < 1 or start.row - i < 1:
                break
            square = self.get_square(start.column - i, start.row - i)
            if square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)

            if not trajectory_found: check_trajectory.append(square)
            if square.has_piece():
                break

        for square in check_trajectory:
            if square.piece.type == 'King':
                trajectory_found = True
        if not trajectory_found:
            check_trajectory.clear()

        for i in range(1, 9):
            if start.column + i > 8 or start.row - i < 1:
                break
            square = self.get_square(start.column + i, start.row - i)
            if square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)
            if not trajectory_found: check_trajectory.append(square)
            if square.has_piece():
                break

        for square in check_trajectory:
            if square.piece.type == 'King':
                trajectory_found = True
        if not trajectory_found:
            check_trajectory.clear()

        for i in range(1, 9):
            if start.column - i < 1 or start.row + i > 8:
                break
            square = self.get_square(start.column - i, start.row + i)
            if square.piece.piece_color == start.piece.piece_color:
                if square.piece.piece_color == 'White':
                    self.protected_squares_white.append(square)
                else:
                    self.protected_squares_black.append(square)
                break
            valid_movements.append(square)

            if not trajectory_found: check_trajectory.append(square)
            if square.has_piece():
                break

        for square in check_trajectory:
            if square.piece.type == 'King':
                trajectory_found = True
        if not trajectory_found:
            check_trajectory.clear()

        if trajectory_found:
            check_trajectory.append(start)
            self.list_of_checking_trajectories.append(check_trajectory)
        return valid_movements

    def valid_queen_movements(self, start):
        # Queen movements are a combination of rook and bishop movements.
        first_set = self.valid_bishop_movements(start)
        second_set = self.valid_rook_movements(start)
        valid_movements = first_set + second_set

        return valid_movements

    def valid_king_movements(self, start):
        # King's moves are limited by whether a square is covered by an enemy piece or not.
        valid_squares = []
        for square in self.squares:
            if abs(square.column - start.column) < 2 and abs(square.row - start.row) < 2:
                if square.has_piece() and square.piece.piece_color == start.piece.piece_color:
                    if square.piece.piece_color == 'White':
                        self.protected_squares_white.append(square)
                    elif square.piece.piece_color == 'Black':
                        self.protected_squares_black.append(square)
                    continue
                if (start.piece.piece_color == 'White' and square in self.protected_squares_black) \
                        or (start.piece.piece_color == 'Black' and square in self.protected_squares_white):
                    continue
                valid_squares.append(square)

        # Restricting any squares covered by enemy pieces
        # TODO: expand and integrate with protected squares field
        for square in self.squares:
            if square.has_piece() and square.piece.piece_color != start.piece.piece_color:
                if square.valid_moves is not None:
                    for possible_move in square.valid_moves:
                        if possible_move in valid_squares:
                            valid_squares.remove(possible_move)
        return valid_squares

    def is_castling_possible(self, color):
        row = 1
        if color == 'Black':
            row = 8


        king_spot = self.get_square(5,row)
        valid_castle = []
        if len(king_spot.piece.past_moves) == 0:
            left_king_spot = self.get_square(3, row)
            left_rook_spot = self.get_square(4, row)
            current_left_rook = self.get_square(1,row)
            print("First")
            if len(current_left_rook.piece.past_moves) == 0 \
                    and not left_king_spot.has_piece() and not left_rook_spot.has_piece() \
                    and not self.get_square(4, row).has_piece():
                print("first firsr")
                valid_castle.append((king_spot,left_king_spot, current_left_rook,left_rook_spot))
                left_king_spot.color = 'Green'
            right_king_spot = self.get_square(7, row)
            right_rook_spot = self.get_square(6, row)
            current_right_rook = self.get_square(8,row)
            if len(current_right_rook.piece.past_moves) == 0 \
                    and not right_rook_spot.has_piece() and not right_king_spot.has_piece():
                valid_castle.append((king_spot,right_king_spot, current_right_rook, right_rook_spot))
                right_king_spot.color = 'Green'
                print("here")
        return valid_castle

    def is_game_over(self):
        # Checks if there are any pieces who have at least one move in all the check_removal trajectories
        # If none, then game is over and the current 'self.turn' is checkmated
        if self.checked:
            for square in self.squares:
                if square.has_piece() and square.piece.piece_color == self.turn:
                    if len(square.valid_moves) != 0:
                        return False
            return True
