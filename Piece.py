import pygame


class Piece:
    def __init__(self, piece_type, piece_color):
        self.type = piece_type
        self.piece_color = piece_color
        self.past_moves = []
        self.is_checking = False

    def get_pic_name(self):
        color = self.piece_color[0]
        piece_type = self.type
        name = color + piece_type + '.png'
        return "ChessPieces/" + name

    def load_pic(self):
        return pygame.image.load(self.get_pic_name()).convert_alpha()

    def promote(self, type):
        self.type = type


if __name__ == '__main__':
    piece = Piece("Bishop", "White")
    print(piece.get_pic_name())
