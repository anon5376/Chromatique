"""Versioned 776-input, side-to-move canonical features and promotion-safe policy.

White is unflipped. Black exchanges piece colours and reflects ranks (sq ^ 56).
State slots: constant 1, own KQ, opponent KQ, EP file/8 or -1,
halfmove/100, twofold repetition. Scores are ALWAYS side-to-move centipawns.
"""
import numpy as np
import chess

VERSION = 'romantic-stm-v1'

def vocabulary():
    moves = set()
    for a in range(64):
        for b in range(64):
            df, dr = abs(a % 8 - b % 8), abs(a // 8 - b // 8)
            if a != b and (not df or not dr or df == dr or sorted((df, dr)) == [1, 2]):
                moves.add(chess.square_name(a) + chess.square_name(b))
    # Both ranks are represented so the encoding is usable outside canonical inference too.
    for rank, target in ((6, 7), (1, 0)):
        for file in range(8):
            for delta in (-1, 0, 1):
                if 0 <= file + delta < 8:
                    for promotion in 'qrbn':
                        moves.add(chess.square_name(rank * 8 + file) + chess.square_name(target * 8 + file + delta) + promotion)
    return sorted(moves)

MOVES = vocabulary()
INDEX = {move: i for i, move in enumerate(MOVES)}

def move_index(move, turn):
    if not turn:
        move = chess.Move(move.from_square ^ 56, move.to_square ^ 56, promotion=move.promotion)
    return INDEX[move.uci()]

def encode(board):
    x = np.zeros(776, dtype=np.float32)
    for sq, piece in board.piece_map().items():
        plane = piece.piece_type - 1 + (0 if piece.color == board.turn else 6)
        x[plane * 64 + (sq if board.turn else sq ^ 56)] = 1
    x[768] = 1
    x[769:773] = [board.has_kingside_castling_rights(board.turn), board.has_queenside_castling_rights(board.turn), board.has_kingside_castling_rights(not board.turn), board.has_queenside_castling_rights(not board.turn)]
    x[773] = -1 if board.ep_square is None else (board.ep_square % 8 + 1) / 8
    x[774] = min(100, board.halfmove_clock) / 100
    x[775] = board.is_repetition(2)
    return x

def leakage_key(board):
    # Ignore counters and repetition: transposed boards cannot cross split boundaries.
    x = encode(board)
    return x[:774].tobytes()
