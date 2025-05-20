import json
import socket
import threading
from typing import Callable

import networking.utils as utils

from game import Move, Piece

class Client:
    def __init__(
        self, 
        on_game_start: Callable[[], None],
        on_move_received: Callable[[Move], None],
        on_opponent_disconnect: Callable[[], None],
        host: str = "127.0.0.1", 
        port: int = 5555
    ) -> None:
        self.__on_game_start = on_game_start
        self.__on_move_received = on_move_received
        self.__on_opponent_disconnect = on_opponent_disconnect
        
        self.__host = host
        self.__port = port
        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#
        self.__connected = True
        
        self.__colour: int | None = None
        self.__receive_thread: threading.Thread | None = None
        
    def get_colour(self) -> int:
        return self.__colour    
        
    def connect(self) -> None:
        try:
            self.__socket.connect((self.__host, self.__port))
            self.__connected = True
            self.__receive_initial_message()
            
            self.__receive_thread = threading.Thread(target=self.__receive_loop)
            self.__receive_thread.start()
            
        except Exception as e:
            self.__log(f"Connection error: {e}")
            self.disconnect()
    
    def __receive_initial_message(self) -> None:
        try:
            msg = self.__socket.recv(1024).decode()
            self.__colour = json.loads(msg).get("colour")
            self.__log(f"Connected as player {Piece.colour_str(self.__colour)}")
        except Exception as e:
            self.__log(f"Failed to read initial message: {e}")
            self.disconnect()
    
    def send_move(self, move: Move) -> None:
        try:
            utils.send_move(self.__socket, move)
        except Exception as e:
            self.__log(f"Failed to send move: {e}")

    def __receive_loop(self) -> None:
        buffer = ""
        while self.__connected:
            try:
                if not (data := self.__socket.recv(4096)):
                    self.__log("Server disconnected")
                    break
                
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.__handle_message(line.strip())
                    
            except (OSError, socket.error) as e:
                if self.__connected:
                    self.__log(f"Receive error: {e}")
                break

        self.disconnect()

    def __handle_message(self, msg: str) -> None:
        if not msg:
            return

        try:
            msg_dict = json.loads(msg)
        except json.JSONDecodeError:
            self.__log("Received invalid JSON")
            return

        if err := msg_dict.get("error"):
            self.__log(f"`Error`: {err}")

        if msg_dict.get("disconnect"):
            self.__log("Opponent disconnected")
            if self.__on_opponent_disconnect:
                self.__on_opponent_disconnect()
            return
            
        if msg_dict.get("begin"):
            self.__log("Game started!")
            if self.__on_game_start:
                self.__on_game_start()
                
        if move_dict := msg_dict.get("move"):
            try:
                move = Move.from_dict(move_dict)
                if self.__on_move_received:
                    self.__on_move_received(move)
            except Exception as e:
                self.__log(f"Failed to parse move: {e}")
                
    def disconnect(self) -> None:
        if self.__connected == False:
            return
        
        self.__connected = False
    
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        
        self.__socket.close()
        
        if (
            self.__receive_thread is not None and
            self.__receive_thread.is_alive() and
            threading.current_thread() != self.__receive_thread
        ):
            self.__receive_thread.join(timeout=1)
            
        self.__log("Connection closed")
         
    def __log(self, msg: str) -> None:
        print(f"[CLIENT] {msg}")