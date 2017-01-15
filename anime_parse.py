#!/usr/bin/env python3
##
# Dakara Project
#

from karaneko.nekoparse import NekoParseAnime
from music_parse import extract_tags

def parse_file_name(file_name):
    """ From a file name, returns a dictionnary with revelant values 
    """
    result = {}
    anime = NekoParseAnime(file_name)
    anime.parse()

    result['title_music'] = anime.title_music
    result['version'] = anime.extras.version
    result['detail'] = anime.details
    result['title_work'] = anime.title_anime
    result['subtitle_work'] = anime.subtitle_anime or ''
    result['work_type_name'] = 'Anime'
    result['work_type_query_name'] = 'anime'

    tags = anime.tags
    if tags.opening:
        result['link_type'] = 'OP'
        result['link_nb'] = tags.opening_nbr
    elif tags.ending:
        result['link_type'] = 'ED'
        result['link_nb'] = tags.ending_nbr

    elif tags.insert_song:
        result['link_type'] = 'IN'

    elif tags.image_song:
        result['link_type'] = 'IS'

    extras = anime.extras
    result['artists'] = []
    if extras.artist:
        result['artists'].append(extras.artist)

    if anime.extras.original_artist:
        result['artists'].append(anime.extras.original_artist)

    detail_video_list = []
    if extras.video:
        detail_video_list.append(extras.video)

    if extras.amv:
        detail_video_list.append(extras.amv)

    if extras.title_video:
        detail_video_list.append(extras.title_video)

    result['detail_video'] = ', '.join(detail_video_list)

    result['episodes'] = extras.episodes

    result['tags'] = extract_tags(tags)

    return result
