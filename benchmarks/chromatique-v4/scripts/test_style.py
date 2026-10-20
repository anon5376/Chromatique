"""Check the material-offer proxy against a sacrifice and an equal queen trade."""
import unittest
import chess

from style import move_features


class StyleAccounting(unittest.TestCase):
    def test_piece_offer_counts_net_concession_and_excludes_equal_trade(self):
        board = chess.Board("rnbq1rk1/ppp2ppp/5n2/3pP3/3P4/3B1N2/PPP2PPP/RNBQ1RK1 w - - 0 8")
        result = move_features(board, chess.Move.from_uci("d3h7"))
        self.assertTrue(result["check"])
        self.assertTrue(result["capture"])
        self.assertEqual(result["material_concession_proxy"], 2)
        board = chess.Board("r2q2k1/8/8/8/8/8/8/3Q2K1 w - - 0 1")
        result = move_features(board, chess.Move.from_uci("d1d8"))
        self.assertEqual(result["material_concession_proxy"], 0)


if __name__ == "__main__":
    unittest.main()
