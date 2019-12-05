import unittest

from anime_parse import parse_file_name


class TestAnimeParse(unittest.TestCase):
    def test_anime_parse_simple(self):
        file_name = "Usagi Drop - OP - Sweet Drops"

        res = parse_file_name(file_name)

        self.assertEqual(res["title_music"], "Sweet Drops")
        self.assertEqual(res["title_work"], "Usagi Drop")
        self.assertEqual(res["link_type"], "OP")

    def test_anime_parse_complex(self):
        file_name = "ABC ~ okaeri - ED36 NSFW SPOIL AMV LONG INST COVER REMIX - Sweet Drops (ARTIST nyako - EP 1423-1532,1600 - VERS Dream - VIDEO Censored - AMV Beah - VTITLE seriously? - (Ultimate))"

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
        self.assertEqual(res["version"], "Dream")
        self.assertEqual(res["detail_video"], "Censored, Beah, seriously?")
        self.assertEqual(res["episodes"], "1423-1532,1600")
        self.assertEqual(res["detail"], "Ultimate")


if __name__ == "__main__":
    unittest.main()
