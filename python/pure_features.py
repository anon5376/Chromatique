"""Pure evaluator inputs: board/state plus geometry, never evaluation terms.

The first 776 slots use romantic-stm-v1. Extra slots contain king coordinates,
king separation/edge distances, occupancy, piece counts and mean piece-to-king
distances. Every output coefficient, including piece values, is learned.
"""
import numpy as np
import chess
from romantic_features import encode as board_features, MOVES, INDEX, move_index

VERSION='chromatique-pure-v1'
DIM=820

def encode(board):
    return extend(board_features(board))

def extend(base):
    x=np.zeros(DIM,np.float32);x[:776]=base
    occupied=np.flatnonzero(x[:768]);squares=occupied%64;planes=occupied//64
    own=int(np.flatnonzero(x[320:384])[0]);enemy=int(np.flatnonzero(x[704:768])[0])
    af,ar,bf,br=own%8,own//8,enemy%8,enemy//8
    x[776:784]=[af/7,ar/7,bf/7,br/7,max(abs(af-bf),abs(ar-br))/7,min(af,7-af,ar,7-ar)/3,min(bf,7-bf,br,7-br)/3,len(occupied)/32]
    for p in range(12):
        sq=squares[planes==p];n=len(sq);x[784+p]=n/8
        if n:
            x[796+p]=np.maximum(abs(sq%8-af),abs(sq//8-ar)).mean()/7
            x[808+p]=np.maximum(abs(sq%8-bf),abs(sq//8-br)).mean()/7
    return x

def family(board):
    # Ignore state counters; also group every geometric symmetry for pawnless
    # endgames. These are partition keys only, never runtime evaluations.
    b=board.copy(stack=False);b.halfmove_clock=0;b.fullmove_number=1
    if not b.turn:b=b.mirror()
    variants=[b]
    if not b.pawns and not b.castling_rights:
        variants=[]
        for flip in (lambda v:v,chess.flip_horizontal,chess.flip_vertical,lambda v:chess.flip_horizontal(chess.flip_vertical(v))):
            t=b.transform(flip);variants.extend((t,t.transform(chess.flip_diagonal)))
    return min(v.board_fen()+' '+str(int(v.turn))+' '+v.castling_xfen()+' '+str(v.ep_square) for v in variants)
