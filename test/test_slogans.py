import unittest
from libs import slogans


class TestSlogans(unittest.TestCase):

    def test_clean_whitespace_should_remove_multiple_inside_spaces(self):
        cleaned_lastname = slogans.clean_whitespace("Albert     Einstein")
        self.assertEqual(cleaned_lastname, "Albert Einstein")

    def test_clean_whitespace_should_remove_trailing_spaces(self):
        cleaned_lastname = slogans.clean_whitespace("Albert Einstein  ")
        self.assertEqual(cleaned_lastname, "Albert Einstein")

    def test_clean_whitespace_should_remove_leading_spaces(self):
        cleaned_lastname = slogans.clean_whitespace("  Albert Einstein")
        self.assertEqual(cleaned_lastname, "Albert Einstein")

if __name__ == '__main__':
    unittest.main()