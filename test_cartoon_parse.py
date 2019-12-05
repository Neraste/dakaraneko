import unittest

from cartoon_parse import parse_file_name


class TestCartoonParse(unittest.TestCase):
    def test_anime_parse_simple(self):
        file_name = "Fruits Basket - OP - FR - Restons Ensemble à Jamais"

        res = parse_file_name(file_name)

        self.assertEqual(res["title_music"], "Restons Ensemble à Jamais")
        self.assertEqual(res["title_work"], "Fruits Basket")
        self.assertEqual(res["link_type"], "OP")
        self.assertEqual(res["version"], "FR")

    def test_anime_parse_complex(self):
        file_name = "ABC ~ okaeri - ED36 NSFW SPOIL AMV LONG INST COVER REMIX - EN - Sweet Drops (ARTIST nyako - EP 1423-1532,1600 - VERS Dream - VIDEO Censored - AMV Beah - VTITLE seriously? - (Ultimate))"

        res = parse_file_name(file_name)

        self.assertEqual(res["title_work"], "ABC")
        self.assertEqual(res["subtitle_work"], "okaeri")
        self.assertEqual(res["link_type"], "ED")
        self.assertEqual(res["link_nb"], 36)
        self.assertCountEqual(
            res["tags"], ["NSFW", "SPOIL", "AMV", "LONG", "INST", "COVER", "REMIX"]
        )
        self.assertEqual(res["title_music"], "Sweet Drops")
        self.assertEqual(res["artists"], ["nyako"])
        self.assertEqual(res["version"], "Dream, EN")
        self.assertEqual(res["detail_video"], "Censored, Beah, seriously?")
        self.assertEqual(res["episodes"], "1423-1532,1600")
        self.assertEqual(res["detail"], "Ultimate")


if __name__ == "__main__":
    unittest.main()
