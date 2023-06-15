import pygame

from Piece import Piece

square_selected = False
letters = ['X', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


class ChessSquare:
    def __init__(self, row, column, piece=Piece("None", "None")):

        self.row = row
        self.column = column
        self.column_letter = letters[column]

        self.rect = pygame.Rect((self.column * 50, self.row * 50), (50, 50))
        self.selected = False
        self.piece = piece

        self.valid_moves = None
        if (row + column) % 2 == 1:
            self.original_color = 'Grey'
        else:
            self.original_color = 'White'
        self.color = self.original_color

    def has_piece(self):
        return self.piece.type != 'None'

    def __str__(self):
        return self.column_letter+str(self.row) + ' ' + self.piece.piece_color + ' ' + self.piece.type

    def column_difference(self, other):
        return self.column - other.column

    def row_difference(self, other):
        return self.row - other.row

    def draw_square(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def check_click(self):
        pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(pos):
                self.selected = True
            else:
                self.color = self.original_color
        else:
            if self.selected:
                self.selected = False
                return True

    def get_pos(self):
        return self.row, self.column

    def display_valid_moves(self):
        for valid_mv in self.valid_moves:
            valid_mv.color = 'Orange'
            if valid_mv.piece.type == 'King':
                valid_mv.color = 'Pink'
        return self.valid_moves

    def check_for_checks(self):
        if self.has_piece():
            for square in self.valid_moves:
                if square.piece.type == 'King':
                    return True
        return False



if __name__ == "__main__":

    list_of_squares = []
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    for j in range(1, 9):
        for i in range(1, 9):
            Black_Square = ChessSquare(i, j)
            print(type(Black_Square.get_pos()))
            list_of_squares.append(Black_Square)
    while True:
        screen.fill('Brown')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for square in list_of_squares:
            square.draw_square(screen)
            square.check_click()

        pygame.display.flip()
