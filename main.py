import sys

import pygame as pg

from game import Board, GameResult, GameState, Piece
import networking

WIN_SIZE = (800, 800)
BANNER_HEIGHT = 96
BG_COLOUR = pg.Color(48, 48, 48)
BANNER_COLOUR = pg.Color(0, 0, 0, 192)
FPS = 60

def main() -> None:
    pg.init()
    pg.font.init()
    font = pg.font.SysFont("Arial", 32, bold=True)
    
    win = pg.display.set_mode(WIN_SIZE)
    pg.display.set_caption("Online Hidden Queen Chess")
    clock = pg.time.Clock()
    
    state = GameState.WAITING
    result = GameResult.NONE
    banner_msg = "Waiting for opponent..."
    
    def _on_game_start():
        nonlocal state, banner_msg
        state = GameState.PLAYING
        banner_msg = ""

    def _on_opponent_disconnect():
        nonlocal state, result, banner_msg
        if state != GameState.GAME_OVER:
            state = GameState.GAME_OVER
            result = GameResult.DISCONNECT
            banner_msg = "Opponent disconnected. You win!"
    
    board = Board()
    board.set_pos_centre(win)
    
    client = networking.Client(_on_game_start, board.apply_move, _on_opponent_disconnect)    
    try:
        client.connect()
    except (ConnectionRefusedError, ConnectionResetError) as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return

    if client.get_colour() is None:
        print("[ERROR] Could not get player colour from server.")
        return
    
    while True:
        clock.tick(FPS)
        
        win.fill(BG_COLOUR)
        board.draw(win)
        
        # Check for game over
        if state == GameState.PLAYING and board.is_game_over():
            state = GameState.GAME_OVER
            result = board.get_game_result()
            
            if result == GameResult.CHECKMATE:
                winner = "White" if board.get_colour_to_move() == Piece.BLACK else "Black"
                banner_msg = f"Game Over: {winner} wins by Checkmate!"
            else:
                banner_msg = f"Game Over: Draw by {result.name.replace('_', ' ').title()}!"
       
        # Draw banner if message to display
        if banner_msg:
            banner_surf = pg.Surface((WIN_SIZE[0], BANNER_HEIGHT), pg.SRCALPHA)
            banner_surf.fill(BANNER_COLOUR)
            win.blit(banner_surf, (0, (WIN_SIZE[1] - BANNER_HEIGHT) // 2))

            text = font.render(banner_msg, True, pg.Color(255, 0, 0))
            text_pos = (WIN_SIZE[0] - text.get_width()) // 2, (WIN_SIZE[1] - text.get_height()) // 2
            win.blit(text, text_pos)
        
        # Event loop
        for e in pg.event.get():
            if e.type == pg.QUIT:
                client.disconnect()
                pg.quit()
                sys.exit(0)
                
            if state == GameState.PLAYING and board.get_colour_to_move() == client.get_colour(): 
                # Handle move events
                move = board.handle_pg_event(e)
                if move and board.is_valid_move(move):
                    client.send_move(move)
                        
        pg.display.flip()

if __name__ == "__main__":
    main()