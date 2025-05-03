import sys

import pygame as pg

import game

WIN_SIZE = (800, 800)
BG_COLOUR = pg.Color(32, 32, 32)
FPS = 60

def main() -> None:
    pg.init()
    win = pg.display.set_mode(WIN_SIZE)
    pg.display.set_caption("Hidden Queen Multiplayer")
    clock = pg.time.Clock()
    
    board = game.Board()
    board.set_pos_centre(win)
        
    while True:
        clock.tick(FPS)
        
        win.fill()
        board.draw(win)
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
                
        pg.display.flip()

if __name__ == "__main__":
    main()