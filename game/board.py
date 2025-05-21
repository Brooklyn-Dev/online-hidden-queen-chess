from typing import List, Tuple

import pygame as pg

from constants import BOARD_SIZE, SQUARE_SIZE

from .castling_rights import CastlingRights
from .game_result import GameResult
from .piece import Piece
from .move import Move, generate_moves, generate_legal_moves
from .utils import is_on_board

from ui.piece_images import PIECE_IMAGES
from ui.promotion_popup import PromotionPopup

class Board:
    LIGHT_SQUARE = pg.Color(208, 208, 208)
    DARK_SQUARE = pg.Color(144, 144, 144)
    ORANGE_HIGHLIGHT = pg.Color(255, 96, 0, 255)
    RED_HIGHLIGHT = pg.Color(255, 0, 0, 255)
    
    def __init__(self) -> None:
        self.__x = 0
        self.__y = 0
        
        self.__flipped = False

        self.__squares = self.__get_initial_squares()
        self.__last_move = None
        self.__colour_to_move = Piece.WHITE
        self.__castling_rights = CastlingRights.ALL
        
        self.__history = []
        self.__position_freq = {}
        
        key = self.__get_position_key()
        self.__position_freq[key] = self.__position_freq.get(key, 0) + 1

        self.__game_result = GameResult.NONE
        self.__fifty_move_count = 0

        self.__selected_square = None
        self.__selected_moves = []
        self.__promotion_popup = None
        self.__pending_promotion_move = None
        
        self.__moves = generate_legal_moves(self, self.__colour_to_move)
    
    @staticmethod
    def __get_initial_squares() -> List[int]:
        return [
            14, 11, 13, 15, 9, 13, 11, 14,
            10, 10, 10, 10, 10, 10, 10, 10,
            *([0] * 32),
            18, 18, 18, 18, 18, 18, 18, 18,
            22, 19, 21, 23, 17, 21, 19, 22
        ]
        
    def flip_board(self) -> None:
        self.__flipped = not self.__flipped
    
    def save_history(self) -> None:
        self.__history.append({
            "squares": self.__squares[:],
            "colour_to_move": self.__colour_to_move,
            "castling_rights": self.__castling_rights,
            "last_move": self.__last_move,
        })
        
    def __get_position_key(self) -> Tuple[Tuple[int], int, int, int]:
        return (
            tuple(self.__squares),
            self.__colour_to_move,
            self.__castling_rights,
            self.__last_move.captured_piece if self.__last_move and self.__last_move.enpassant else Piece.NONE
        )
        
    def __increment_position_key(self) -> None:
        key = self.__get_position_key()
        self.__position_freq[key] = self.__position_freq.get(key, 0) + 1
        
    def set_pos_centre(self, win: pg.Surface) -> None:
        self.__x = (win.get_width() - BOARD_SIZE) // 2
        self.__y = (win.get_height() - BOARD_SIZE) // 2
        self.__rect = pg.Rect(self.__x, self.__y, BOARD_SIZE, BOARD_SIZE)

    def get_square(self, index: int) -> int:
        if not is_on_board(index):
            raise IndexError()

        return self.__squares[index]

    def get_colour_to_move(self) -> int:
        return self.__colour_to_move
    
    def get_last_move(self) -> Move | None:
        return self.__last_move

    def can_castle(self, castling_right: int) -> bool:
        return self.__castling_rights & castling_right

    def get_game_result(self) -> int:
        return self.__game_result

    def is_game_over(self) -> bool:
        return self.__game_result != GameResult.NONE

    def __draw_square(self, win: pg.Surface, x: int, y: int, rank: int, file: int) -> None:
        is_light_square = (rank + file) % 2 != 0
        colour = Board.LIGHT_SQUARE if is_light_square else Board.DARK_SQUARE
        square_index = rank * 8 + file
        
        if self.__selected_square == square_index:
            colour = colour.lerp(Board.ORANGE_HIGHLIGHT, 0.6)
        elif any(m.end == square_index for m in self.__selected_moves):
            colour = colour.lerp(Board.RED_HIGHLIGHT, 0.5)
            
        pg.draw.rect(win, colour, pg.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))  
        
    def __draw_piece(self, win: pg.Surface, x: int, y: int, piece: int) -> None:
        image = PIECE_IMAGES[Piece.colour(piece)][Piece.piece_type(piece)]
        win.blit(image, (x, y))
        
    def draw(self, win: pg.Surface) -> None:
        if self.__flipped:
            for rank in range(8):
                for file in range(8):
                    x = self.__x + (7 - file) * SQUARE_SIZE
                    y = self.__y + rank * SQUARE_SIZE
            
                    self.__draw_square(win, x, y, rank, file)
                    
                    piece = self.__squares[rank * 8 + file]
                    if piece != 0:
                        self.__draw_piece(win, x, y, piece) 
        else:
            for rank in range(8):
                for file in range(8):
                    x = self.__x + file * SQUARE_SIZE
                    y = self.__y + (7 - rank) * SQUARE_SIZE
            
                    self.__draw_square(win, x, y, rank, file)
                    
                    piece = self.__squares[rank * 8 + file]
                    if piece != 0:
                        self.__draw_piece(win, x, y, piece)
                    
        if self.__promotion_popup is not None:
            self.__promotion_popup.draw(win) 
            
    def handle_pg_event(self, e: pg.Event) -> Move | None:            
        if e.type == pg.MOUSEBUTTONDOWN:
            if self.__promotion_popup is not None:
                piece_type = self.__promotion_popup.poll(e)
                if piece_type is not None:
                    move = self.__pending_promotion_move
                    move.promotion_piece = piece_type | self.__colour_to_move
                    
                    self.__clear_promotion()
                    return move
                
                self.__clear_promotion()
            
            return self.__handle_mouse_down(e)
                    
    def __handle_mouse_down(self, e: pg.Event) -> Move | None:
        mx, my = e.pos
        
        if not self.__rect.collidepoint(mx, my):
            self.__clear_selection()
            return
        
        rel_x = mx - self.__x
        rel_y = my - self.__y
                
        if self.__flipped:
            file = 7 - (rel_x // SQUARE_SIZE)
            rank = rel_y // SQUARE_SIZE
        else:
            file = rel_x // SQUARE_SIZE
            rank = 7 - (rel_y // SQUARE_SIZE)
        
        index = rank * 8 + file
        
        if not is_on_board(index):
            return
        
        self.__clear_promotion()
        
        if self.__selected_square is not None:
            for move in self.__get_legal_moves_from(self.__selected_square):
                if move.end == index:
                    self.__clear_selection()
                    
                    if move.promotion:
                        self.create_promotion_popup(move)
                        return None
                
                    return move
    
        piece = self.__squares[index]
        if piece != Piece.NONE and Piece.colour(piece) == self.__colour_to_move:
            self.__selected_square = index
            self.__selected_moves = self.__get_legal_moves_from(index)
        else:
            self.__clear_selection()   
    
    def __clear_selection(self) -> None:
        self.__selected_square = None
        self.__selected_moves.clear()
        self.__clear_promotion()
    
    def __clear_promotion(self) -> None:
        self.__promotion_popup = None
        self.__pending_promotion_move = None
    
    def has_pending_promotion(self) -> bool:
        return self.__pending_promotion_move is not None
    
    def is_valid_move(self, move: Move) -> bool:
        for m in self.__moves:
            if move == m:
                return True
            
        return False

    def create_promotion_popup(self, move: Move) -> None:
        rank, file = divmod(move.end, 8)
        if self.__flipped:
            x = self.__x + (7 - file) * SQUARE_SIZE
            y = self.__y + rank * SQUARE_SIZE
        else:
            x = self.__x + file * SQUARE_SIZE
            y = self.__y + (7 - rank) * SQUARE_SIZE
        
        self.__pending_promotion_move = move
        self.__promotion_popup = PromotionPopup(self.__colour_to_move, (x, y), lambda piece_type: piece_type)
    
    def apply_move(self, move: Move) -> None:
        self.__fifty_move_count += 1
        if Piece.piece_type(move.piece) == Piece.PAWN or move.captured_piece != Piece.NONE:
            self.__fifty_move_count = 0
        
        self.make_move(move)
        self.__clear_selection()
        self.__moves = generate_legal_moves(self, self.__colour_to_move)
        self.__check_game_end()
        
    def make_move(self, move: Move) -> None:
        self.save_history()
        
        if move.promotion:
            self.__squares[move.end] = move.promotion_piece
            self.__squares[move.start] = Piece.NONE
        elif move.enpassant:
            direction = 8 if self.__colour_to_move == Piece.WHITE else -8
            captured_square = move.end - direction 
            self.__squares[captured_square] = Piece.NONE
            self.__squares[move.end] = move.piece
        elif move.castling:
            if self.__colour_to_move == Piece.WHITE:
                self.__castling_rights &= CastlingRights.B
            else:
                self.__castling_rights &= CastlingRights.W
                
            match move.castling:
                case CastlingRights.WK:
                    self.__squares[4] = Piece.NONE
                    self.__squares[7] = Piece.NONE
                    self.__squares[6] = Piece.KING | Piece.WHITE
                    self.__squares[5] = Piece.ROOK | Piece.WHITE
                case CastlingRights.WQ:
                    self.__squares[4] = Piece.NONE
                    self.__squares[0] = Piece.NONE
                    self.__squares[2] = Piece.KING | Piece.WHITE
                    self.__squares[3] = Piece.ROOK | Piece.WHITE
                case CastlingRights.BK:
                    self.__squares[60] = Piece.NONE
                    self.__squares[63] = Piece.NONE
                    self.__squares[62] = Piece.KING | Piece.BLACK
                    self.__squares[61] = Piece.ROOK | Piece.BLACK
                case CastlingRights.BQ:
                    self.__squares[60] = Piece.NONE
                    self.__squares[56] = Piece.NONE
                    self.__squares[58] = Piece.KING | Piece.BLACK
                    self.__squares[59] = Piece.ROOK | Piece.BLACK
        else:
            piece_type = Piece.piece_type(move.piece)
            captured_piece_type = Piece.piece_type(move.captured_piece)
            
            if piece_type == Piece.KING:
                if Piece.colour(move.piece) == Piece.WHITE:
                    self.__castling_rights &= CastlingRights.B
                else:
                    self.__castling_rights &= CastlingRights.W
                    
            elif piece_type == Piece.ROOK:
                if move.start == 0:
                    self.__castling_rights &= ~CastlingRights.WQ
                elif move.start == 7:
                    self.__castling_rights &= ~CastlingRights.WK
                elif move.start == 56:
                    self.__castling_rights &= ~CastlingRights.BQ
                elif move.start == 63:
                    self.__castling_rights &= ~CastlingRights.BK
                    
            if captured_piece_type == Piece.ROOK:
                if move.end == 0:
                    self.__castling_rights &= ~CastlingRights.WQ
                elif move.end == 7:
                    self.__castling_rights &= ~CastlingRights.WK
                elif move.end == 56:
                    self.__castling_rights &= ~CastlingRights.BQ
                elif move.end == 63:
                    self.__castling_rights &= ~CastlingRights.BK
            
            self.__squares[move.end] = move.piece
        
        self.__squares[move.start] = Piece.NONE
        
        self.__last_move = move
        self.__colour_to_move = Piece.WHITE if self.__colour_to_move == Piece.BLACK else Piece.BLACK
        self.__increment_position_key()
        
    def unmake_move(self) -> None:
        if not self.__history:
            return
        
        last_state = self.__history.pop()
        
        self.__squares = last_state["squares"]
        self.__colour_to_move = last_state["colour_to_move"]
        self.__castling_rights = last_state["castling_rights"]
        self.__last_move = last_state["last_move"]
        
        key = self.__get_position_key()
        if key in self.__position_freq:
            self.__position_freq[key] -= 1
            if self.__position_freq[key] == 0:
                del self.__position_freq[key]
                
    def __get_legal_moves_from(self, square: int) -> List[Move]:
        return [m for m in self.__moves if m.start == square]
    
    def get_king_square(self, colour: int) -> int:
        return next(i for i, p in enumerate(self.__squares) if p == (Piece.KING | colour))
    
    def is_in_check(self, colour: int) -> bool:
        king_square = self.get_king_square(colour)
        
        opp_moves = generate_moves(self, Piece.opposite_colour(colour), include_king=False)
        for move in opp_moves:
            if move.end == king_square:
                return True
            
        return False
    
    def __is_insufficient_material(self) -> bool:
        pieces = [p for p in self.__squares if p != Piece.NONE]
        material = [Piece.piece_type(p) for p in pieces]
        
        if material == [Piece.KING, Piece.KING]:
            return True
        
        if len(material) == 3:
            return Piece.KNIGHT in material or Piece.BISHOP in material
        
        return False
    
    def __is_threefold_repetition(self) -> bool:
        for count in self.__position_freq.values():
            if count >= 3:
                return True
            
        return False
    
    def __check_game_end(self) -> None:
        if len(self.__moves) == 0:
            if self.is_in_check(self.__colour_to_move):
                self.__game_result = GameResult.CHECKMATE
            else:
                self.__game_result = GameResult.STALEMATE
        elif self.__is_insufficient_material():
            self.__game_result = GameResult.INSUFFICIENT_MATERIAL
        elif self.__fifty_move_count >= 50:
            self.__game_result = GameResult.FIFTY_MOVE_RULE
        elif self.__is_threefold_repetition():
            self.__game_result = GameResult.THREEFOLD_REPETITION