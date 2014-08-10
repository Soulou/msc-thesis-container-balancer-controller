import unittest
from balance import BestFitDecreasing
from balance import Bin

class TestBestFitDecreasing(unittest.TestCase):
    def test_pack(self):
        items = [[0.75, 0.10, 0.01], [0.20, 0.3, 0.01], [0.40, 0.12, 0.10], [0.30, 0.10, 0.5]]
        bins = [Bin("localhost", [1,1,1]), Bin("localhost", [1,1,1]), Bin("localhost", [1,1,1])]
        result = BestFitDecreasing.pack(items, bins)
        self.assertEqual(result['mapping'], [0, 2, 1, 1])
