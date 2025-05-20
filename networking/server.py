import json
import socket
import threading
from typing import Dict

from .game_room import GameRoom
import networking.utils as utils

from game import Move, Piece

class Server:
    def __init__(self, host: str = "127.0.0.1", port: str = 5555) -> None:
        self.__host = host
        self.__port = port
        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((self.__host, self.__port))
        self.__socket.listen()
        
        self.__rooms: Dict[int, GameRoom] = {}
        self.__waiting_room: GameRoom | None = None
        self.__next_room_id = 1
        
        self.__lock = threading.Lock()
        
        self.__log(f"Initialised on {self.__host}:{self.__port}")
        
    def start(self) -> None:
        self.__log("Listening for connections...")
        while True:
            conn, addr = self.__socket.accept()
            self.__log(f"New Connection from {addr}")
            threading.Thread(target=self.__assign_to_room, args=(conn,), daemon=True).start()
            
    def __assign_to_room(self, conn: socket.socket) -> None:
        with self.__lock:
            if self.__waiting_room is None:
                # New room
                room = GameRoom(room_id=self.__next_room_id)
                self.__next_room_id += 1
                room.players.append(conn)
                self.__waiting_room = room
                colour = Piece.WHITE
            else:
                # Join waiting room
                room = self.__waiting_room
                room.players.append(conn)
                self.__rooms[room.room_id] = room
                self.__waiting_room = None
                colour = Piece.BLACK

        # Notify the player of their colour
        try:
            conn.sendall(f'{{"colour": {colour}}}\n'.encode())
        except:
            self.__log("Failed to notify player of their colour, closing connection")
            self.__handle_disconnect(room, conn, colour)
            return
        
        # Notify both players that the game has started
        if len(room.players) == 2:
            for player in room.players:
                try:
                    player.sendall(b'{"begin": true}\n')
                except:
                    self.__log("Failed to notify game start")
            
        threading.Thread(target=self.__handle_client, args=(room, conn, colour), daemon=True).start()
            
    def __handle_client(self, room: GameRoom, conn: socket.socket, colour: int) -> None:
        try:
            buffer = ""
            while True:      
                if not (data := conn.recv(4096)):
                    break
                  
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.__handle_message(line.strip(), room, conn, colour)
        
        except Exception as e:
            self.__log(f"Error in client thread: {e}")
        
        finally:
            self.__handle_disconnect(room, conn, colour) 

    def __handle_message(self, msg: str, room: GameRoom, conn: socket.socket, colour: int) -> None:
        if not msg:
            return

        try:
            msg_dict = json.loads(msg)
        except json.JSONDecodeError:
            self.__log("Received invalid JSON")
            return

        if move_json := msg_dict.get("move"):
            try:
                move = Move.from_dict(move_json)
            except Exception:
                utils.send_error(conn, "Invalid move format")
                return

            with self.__lock:
                board = room.board
                expected_colour = board.get_colour_to_move()

                if colour != expected_colour:
                    utils.send_error(conn, "Not your turn")
                    return

                if board.is_valid_move(move):
                    board.apply_move(move)
                    self.__broadcast_move(room, move)
                else:
                    utils.send_error(conn, "Invalid move")

    def __handle_disconnect(self, room: GameRoom, conn: socket.socket, colour: int) -> None:
        with self.__lock:
            if conn in room.players:
                room.players.remove(conn)

                    # If only one player left, notify and delete room
                if room in self.__rooms.values():
                    if room.players:
                        try:
                            room.players[0].sendall(b'{"disconnect": true}\n')
                        except Exception:
                            pass
                    self.__rooms.pop(room.room_id, None)

                # If the disconnected player was in waiting_room
                if self.__waiting_room is room:
                    self.__waiting_room = None

        conn.close()
        self.__log(f"Player {Piece.colour_str(colour)} disconnected from room {room.room_id}")
          
    def __broadcast_move(self, room: GameRoom, move: Move) -> None:
        for player in room.players:
            try:
                utils.send_move(player, move)
            except Exception:
                self.__log("Failed to send move to a player")
                
    def __log(self, msg: str) -> None:
        print(f"[SERVER] {msg}")
        
if __name__ == "__main__":
    server = Server()
    server.start()