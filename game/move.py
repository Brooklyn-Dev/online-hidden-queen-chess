from copy import deepcopy
from dataclasses import asdict, dataclass
import json
from typing import Dict, List

from .castling_rights import CastlingRights
from .piece import Piece
from .utils import is_on_board

@dataclass
class Move:
    start: int
    end: int
    piece: int
    captured_piece: int | None
    promotion: bool = False
    promotion_piece: int = Piece.NONE
    enpassant: bool = False
    castling: bool = False
    
    @staticmethod
    def from_dict(data: Dict) -> "Move":
        return Move(**data)
    
    @staticmethod
    def to_json(move: "Move") -> str:
        return json.dumps(asdict(move))
    
    @staticmethod
    def from_json(data: str) -> "Move":
        return Move(**json.loads(data))
    
def _is_move_legal(board: "Board", colour: int, move: Move):
    board_copy = deepcopy(board)
    board_copy.make_move(move)
        
    king_square = board_copy.get_king_square(colour)
        
    opp_responses = generate_moves(board_copy, Piece.opposite_colour(colour))
    if not any([res for res in opp_responses if res.end == king_square]):
        return move
    
def generate_legal_moves(board: "Board", colour: int) -> List[Move]:
    moves = generate_moves(board, colour)
    legal_moves = []
    
    for move in moves:
        if move.promotion:
            for promo_type in (Piece.QUEEN, Piece.ROOK, Piece.BISHOP, Piece.KNIGHT):
                promo_move = Move(move.start, move.end, move.piece, move.captured_piece, promotion=True)
                promo_move.promotion_piece = promo_type | colour
                        
                if _is_move_legal(board, colour, promo_move):
                    legal_moves.append(promo_move)
        else:
            if _is_move_legal(board, colour, move):
                legal_moves.append(move)
            
    return legal_moves

def generate_moves(board: "Board", colour: int, include_king: bool = True) -> List[Move]:
    moves = []
    
    for square in range(64):
        piece = board.get_square(square)
        if Piece.colour(piece) != colour:
            continue
        
        piece_type = Piece.piece_type(piece)

        if piece_type == Piece.PAWN:
            moves += _generate_pawn_moves(board, square, piece)
        elif piece_type == Piece.KING and include_king:
            moves += _generate_king_moves(board, square, piece)
            moves += _generate_castling_moves(board, piece)
        elif piece_type == Piece.KNIGHT:
            moves += _generate_knight_moves(board, square, piece)
        elif Piece.is_sliding_piece(piece):
            moves += _generate_sliding_moves(board, square, piece)
            
    return moves

def _generate_king_moves(board: "Board", square: int, piece: int) -> List[Move]:
    moves = []
    start_file = square % 8
    directions = (-9, -8, -7, -1, 1, 7, 8, 9)
        
    for direction in directions:
        target = square + direction
        if not is_on_board(target):
            continue           
        
        # Check for wrapping
        target_file = target % 8
        df = abs(target_file - start_file) 
        if direction not in [-8, 8] and df != 1:
            continue
        
        target_piece = board.get_square(target)
        if target_piece == Piece.NONE or Piece.colour(piece) != Piece.colour(target_piece):
            moves.append(Move(square, target, piece, target_piece))
            
    return moves

def _generate_castling_moves(board: "Board", piece: int) -> List[Move]:
    if board.is_in_check(Piece.colour(piece)):
        return []

    moves = []
    is_white = Piece.colour(piece) == Piece.WHITE
    rank = 0 if is_white else 7
    base_index = rank * 8
    king_start = base_index + 4

    short_right = CastlingRights.WK if is_white else CastlingRights.BK
    short_clear_files = (5, 6)
    if board.can_castle(short_right) and all(board.get_square(base_index + f) == Piece.NONE for f in short_clear_files):
        moves.append(Move(king_start, king_start + 2, piece, Piece.NONE, castling=short_right))

    long_right = CastlingRights.WQ if is_white else CastlingRights.BQ
    long_clear_files = (1, 2, 3)
    if board.can_castle(long_right) and all(board.get_square(base_index + f) == Piece.NONE for f in long_clear_files):
        moves.append(Move(king_start, king_start - 2, piece, Piece.NONE, castling=long_right))
 
    return moves

def _generate_pawn_moves(board: "Board", square: int, piece: int) -> List[Move]:
    moves = []
    colour = Piece.colour(piece)
    rank, file = divmod(square, 8)
    
    direction = 1 if colour == Piece.WHITE else -1
    start_rank = 1 if colour == Piece.WHITE else 6
    promotion_rank = 7 if colour == Piece.WHITE else 0
    
    one_forward = square + direction * 8
    if is_on_board(one_forward) and board.get_square(one_forward) == Piece.NONE:
        if rank + 1 == promotion_rank:
            moves.append(Move(square, one_forward, piece, Piece.NONE, promotion=True))  # 1 step forward + promotion
        else:
            moves.append(Move(square, one_forward, piece, Piece.NONE))  # 1 step forward
        
        if rank == start_rank:
            two_forward = one_forward + direction * 8
            if board.get_square(two_forward) == Piece.NONE:
                moves.append(Move(square, two_forward, piece, Piece.NONE))  # 2 steps forward       
                
    for df in [-1, 1]:
        if not (0 <= file + df < 8):
            continue
        
        target = one_forward + df
        if not is_on_board(target):
            continue
        
        target_piece = board.get_square(target)
        if target_piece != Piece.NONE and Piece.colour(target_piece) != colour:
            if rank + direction == promotion_rank:
                moves.append(Move(square, target, piece, target_piece, promotion=True))  # 1 forward diagonal + capture + promotion
            else:
                moves.append(Move(square, target, piece, target_piece))  # 1 forward diagonal + capture
                
    # Enpassant
    last_move = board.get_last_move()
    if last_move is not None and Piece.piece_type(last_move.piece) == Piece.PAWN:
        diff = abs(last_move.start - last_move.end)
        if diff == 16:  # 2 steps forward
            last_end_rank, last_end_file = divmod(last_move.end, 8)
            if last_end_rank == rank and abs(last_end_file - file) == 1:
                ep_target = last_move.end + direction * 8  # Square behind opponent pawn
                if is_on_board(ep_target):
                    moves.append(Move(square, ep_target, piece, last_move.piece, enpassant=True))
            
    return moves

def _generate_knight_moves(board: "Board", square: int, piece: int) -> List[Move]:
    moves = []
    start_rank = square // 8
    directions = (-17, -15, -10, -6, 6, 10, 15, 17)
        
    for direction in directions:
        target = square + direction
        if not is_on_board(target):
            continue           
        
        # Check for wrapping
        target_rank = target // 8
        dr = abs(target_rank - start_rank)
        if direction in [-17, -15, 15, 17] and dr != 2:
            continue
        if direction in [-10, -6, 6, 10] and dr != 1:
            continue
        
        target_piece = board.get_square(target)
        if target_piece == Piece.NONE or Piece.colour(target_piece) != Piece.colour(piece):
            moves.append(Move(square, target, piece, target_piece))
            
    return moves

def _generate_sliding_moves(board: "Board", square: int, piece: int) -> List[Move]:
    directions = []
    if Piece.can_slide_diagonal(piece):
        directions += [-9, -7, 7, 9]
    if Piece.can_slide_orthogonal(piece):
        directions += [-8, -1, 1, 8]
         
    moves = []
    start_rank, start_file = divmod(square, 8)

    for direction in directions:
        for step in range(1, 8):
            target = square + direction * step
            if not is_on_board(target):
                break

            # Check wrapping
            target_rank, target_file = divmod(target, 8)
            dr, df = abs(target_rank - start_rank), abs(target_file - start_file)
            if direction in [-9, -7, 7, 9] and dr != df:
                break
            if direction in [-1, 1] and dr != 0:
                break

            target_piece = board.get_square(target)
            if target_piece == Piece.NONE:
                moves.append(Move(square, target, piece, target_piece))
            else:
                if Piece.colour(target_piece) != Piece.colour(piece):
                    moves.append(Move(square, target, piece, target_piece))
                break

    return moves