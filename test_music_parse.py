import unittest

from music_parse import parse_file_name


class TestMusicParse(unittest.TestCase):
    def test_music_parse_simple(self):
        file_name = "supercell - PV - Kimi no shiranai monogatari"

        res = parse_file_name(file_name)

        self.assertEqual(res["title_music"], "Kimi no shiranai monogatari")
        self.assertEqual(res["artists"], ["supercell"])
        self.assertEqual(res["tags"], ["PV"])

    def test_music_parse_complex(self):
        file_name = "Git, gud feat. bar, foo - LIVE NSFW SPOIL LONG INST COVER REMIX - Sweet Drops (OP42 Love love - OARTIST nyako - VERS Dream - VIDEO Censored - AMV Beah - VTITLE seriously? - (Ultimate))"

        res = parse_file_name(file_name)

        self.assertCountEqual(res["artists"], ["Git", "gud", "foo", "bar", "nyako"])
        self.assertCountEqual(
            res["tags"], ["NSFW", "SPOIL", "LIVE", "LONG", "INST", "COVER", "REMIX"]
        )
        self.assertEqual(res["title_music"], "Sweet Drops")
        self.assertEqual(res["link_type"], "OP")
        self.assertEqual(res["link_nb"], 42)
        self.assertEqual(res["title_work"], "Love love")
        self.assertEqual(res["version"], "Dream")
        self.assertEqual(res["detail_video"], "Censored, Beah, seriously?")
        self.assertEqual(res["detail"], "Ultimate")


if __name__ == "__main__":
    unittest.main()
