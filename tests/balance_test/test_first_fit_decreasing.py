import unittest
from balance import FirstFitDecreasing
from balance import Bin

class TestFirstFitDecreasing(unittest.TestCase):
    def test_pack(self):
        items = [[0.75, 0.10, 0.01], [0.20, 0.3, 0.01], [0.65, 0.12, 0.10], [0.30, 0.10, 0.5]]
        bins = [Bin("localhost", [1,1,1]), Bin("localhost", [1,1,1]), Bin("localhost", [1,1,1])]
        result = FirstFitDecreasing.pack(items, bins)
        self.assertEqual(result['mapping'], [0, 2, 1, 2])
