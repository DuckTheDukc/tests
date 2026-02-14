import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = Calculator()
    
    def test_plus(self):
        self.assertEqual(self.calculator.plus(23,7), 30)

    def test_plus(self):
        self.assertNotEqual(self.calculator.plus(2000000,7), 1)

    def test_minus(self):
        self.assertEqual(self.calculator.minus(70, 3), 67)

    def test_minus(self):
        self.assertNotEqual(self.calculator.minus(2, 3), 500)

    def test_multiply(self):
        self.assertEqual(self.calculator.multiply(5,5), 25)

    def test_multiply(self):
        self.assertNotEqual(self.calculator.multiply(5,5), 99)

    def test_divide(self):
        self.assertEqual(self.calculator.divide(70,7), 10)

    def test_divide(self):
        self.assertEqual(self.calculator.divide(5,0), "на 0 делить нельзя")

if __name__ == "__main__":
    unittest.main()