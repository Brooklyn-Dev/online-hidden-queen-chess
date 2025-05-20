from typing import Any, Callable, Tuple

import pygame as pg

class ImageButton:    
    def __init__(self, image: pg.Surface, pos: Tuple[int, int], callback: Callable, callback_args: Tuple[Any] | None = None) -> None:
        self.__image = image
        self.__rect = image.get_rect(topleft=pos)
        self.__callback = callback
        self.__callback_args = callback_args

    def draw(self, win: pg.Surface) -> None: 
        win.blit(self.__image, self.__rect)

    def poll(self, e: pg.Event) -> bool:
        if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
            if self.__rect.collidepoint(e.pos):
                return True
            
        return False

    def invoke_callback(self) -> None:
        if self.__callback_args is not None:
            return self.__callback(*self.__callback_args)
        else:
            return self.__callback()