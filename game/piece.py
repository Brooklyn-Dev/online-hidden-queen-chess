class Piece:
    NONE = 0b00000  # 0
    KING = 0b00001  # 1
    PAWN = 0b00010  # 2
    KNIGHT = 0b00011  # 3
    BISHOP = 0b00101  # 5
    ROOK = 0b00110  # 6
    QUEEN = 0b00111  # 7

    WHITE = 0b01000  # 8
    BLACK = 0b10000  # 16
    
    __TYPE_MASK = 0b00111  # 7
    __COLOUR_MASK = 0b11000  # 24 
    
    @staticmethod
    def is_white(piece: int) -> int:
        return piece & Piece.WHITE
    
    @staticmethod
    def is_black(piece: int) -> int:
        return piece & Piece.BLACK
    
    @staticmethod
    def colour(piece: int) -> int:
        return piece & Piece.__COLOUR_MASK
    
    @staticmethod
    def opposite_colour(colour: int) -> int:
        return Piece.BLACK if colour == Piece.WHITE else Piece.WHITE
    
    @staticmethod
    def is_sliding_piece(piece: int) -> int:
        return (piece & 0b00100) == 0b00100    
    
    @staticmethod
    def can_slide_diagonal(piece: int) -> int:
        return (piece & 0b00101) == 0b00101
    
    @staticmethod
    def can_slide_orthogonal(piece: int) -> int:
        return (piece & 0b00110) == 0b00110
    
    @staticmethod
    def piece_type(piece: int) -> int:
        return piece & Piece.__TYPE_MASK
    
    @staticmethod
    def piece_letter(piece: int) -> str:
        return {
            Piece.KNIGHT: "N",
            Piece.BISHOP: "B",
            Piece.ROOK: "R",
            Piece.QUEEN: "Q",
            Piece.KING: "K",
        }.get(piece, "")