#!/usr/bin/env python3
##
# Dakara Project
#

from karaneko.nekoparse import NekoParseCartoon, NekoParseTagsCartoon


def extract_tags(tags):
    """ From the tags dictionnary, returns list of tags
    """
    tags_list = []

    for tag in NekoParseTagsCartoon.tags:
        if tag["category"] == "use":
            # ignore use tags
            continue

        if getattr(tags, tag["name"]):
            tags_list.append(tag["serializer"])

    return tags_list


def parse_file_name(file_name):
    """ From a file name, returns a dictionnary with revelant values 
    """
    result = {}
    cartoon = NekoParseCartoon(file_name)
    cartoon.parse()

    result["title_music"] = cartoon.title_music or cartoon.title_cartoon
    result["version"] = ", ".join(
        v for v in (cartoon.extras.version, cartoon.language) if v
    )
    result["detail"] = cartoon.details
    result["title_work"] = cartoon.title_cartoon
    result["subtitle_work"] = cartoon.subtitle_cartoon or ""
    result["work_type_query_name"] = "cartoon"

    tags = cartoon.tags
    if tags.opening:
        result["link_type"] = "OP"
        result["link_nb"] = tags.opening_nbr

    elif tags.ending:
        result["link_type"] = "ED"
        result["link_nb"] = tags.ending_nbr

    elif tags.insert_song:
        result["link_type"] = "IN"

    elif tags.image_song:
        result["link_type"] = "IS"

    extras = cartoon.extras
    result["artists"] = []
    if extras.artist:
        result["artists"].append(extras.artist)

    if cartoon.extras.original_artist:
        result["artists"].append(cartoon.extras.original_artist)

    detail_video_list = []
    if extras.video:
        detail_video_list.append(extras.video)

    if extras.amv:
        detail_video_list.append(extras.amv)

    if extras.title_video:
        detail_video_list.append(extras.title_video)

    result["detail_video"] = ", ".join(detail_video_list)

    result["episodes"] = extras.episodes

    result["tags"] = extract_tags(tags)

    return result
