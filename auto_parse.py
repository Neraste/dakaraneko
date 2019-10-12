#!/usr/bin/env python3
##
# Dakara Project
#

import re
from anime_parse import parse_file_name as anime_parse_file_name
from music_parse import parse_file_name as music_parse_file_name
from karaneko.nekoparse import ConventionError

REGEX_TAGS = r".*? - (?P<tags>.*?) - .*"
REGEX_ANIME_TAGS = r"^(OP\d*|ED\d*|INS|IS)$"


def parse_file_name(file_name):
    """ AutoDetect file name as anime or music
    """
    search_tags = re.search(REGEX_TAGS, file_name)

    if search_tags:
        tags = search_tags.group("tags").split(" ")

        if any(re.match(REGEX_ANIME_TAGS, tag) for tag in tags):
            return anime_parse_file_name(file_name)

        else:
            return music_parse_file_name(file_name)

    else:
        raise ConventionError("Unparsable name")
