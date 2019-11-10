##
# Dakara Project
#

from anime_parse import parse_file_name as parse_file_name_music

def parse_file_name(file_name):
    """ From a file name, returns a dictionnary with revelant values 
    """
    result = parse_file_name_music(file_name, scrap=False)
    result['work_type_query_name'] = 'live-action'

    return result
