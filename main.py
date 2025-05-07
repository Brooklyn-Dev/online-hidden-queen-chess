import sys

import pygame as pg

import game

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
    
    board = game.Board()
    board.set_pos_centre(win)
    
    state = game.GameState.PLAYING
    result = game.GameResult.NONE
    
    while True:
        clock.tick(FPS)
        
        win.fill(BG_COLOUR)
        board.draw(win)
        
        if state == game.GameState.PLAYING and board.is_game_over():
            state = game.GameState.GAME_OVER
            result = board.get_game_result()
            
        if result != game.GameResult.NONE:
            winner = "White" if board.get_colour_to_move() == game.Piece.BLACK else "Black"
            
            msg = ""  
            if result == game.GameResult.CHECKMATE:
                msg = f"Game Over: {winner} wins by Checkmate!"
            else:
                msg = f"Game Over: Draw by {result.name.replace('_', ' ').title()}!"
            
            banner_surf = pg.Surface((WIN_SIZE[0], BANNER_HEIGHT), pg.SRCALPHA)
            banner_surf.fill(BANNER_COLOUR)
            win.blit(banner_surf, (0, (WIN_SIZE[1] - BANNER_HEIGHT) // 2))
             
            text = font.render(msg, True, pg.Color(255, 0, 0))
            text_pos = (WIN_SIZE[0] - text.get_width()) // 2, (WIN_SIZE[1]- text.get_height()) // 2
            win.blit(text, text_pos)
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
                
            if state == game.GameState.PLAYING:
                board.handle_pg_event(e)
                
        pg.display.flip()

if __name__ == "__main__":
    main()