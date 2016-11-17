#!/usr/bin/env python2
# -*- coding: utf8 -*-

""" NekoParse

La bibliothèque de parsage des fichiers karaoké du Cartel. Elle permet de
récupérer les infos d'un titre en dictionnaire et de transformer un
dictionnaire d'info en titre selon la convention de nommage.

Musique - music
    [Compositeur feat.] Chanteur - Genre - Titre musique [(Détail)]

Anime - anime
    Titre anime original [~ Sous titre] - Genre - Titre musique [(Détail)]

Dessins animés - cartoon
    Titre dessin animé original [~ Sous titre] - Genre - Langue [ - Titre musique] [(Détail)]

Genre
    OP#   OPening #
    ED#   EnDing #
    INS   INSert song
    IS    Image Song

    PV    Promotionnal Video
    AMV   Anime Music Video
    LIVE  version LIVE
    SPOIL vidéo présentant du SPOIL

    COURT version COURte
    LONG  version LONGue
    INST  piste INSTrumentale disponible
    COVER COVER de la version originale
    REMIX REMIX de la musique originale
"""


##
# Imports
#



import re


##
# Flags
#


# exécuter les tests de conformité aux conventions sur chaque kara
check = True


##
# Regex
#


# Recherche le pattern de musique
music_pattern = r"^(?:(?P<composer>.+?) feat\. )?(?P<singer>.+?) - (?P<genre>.+?) - (?P<title_music>.+?)(?: \((?P<detail>.*)\))?$"
music_re = re.compile(music_pattern, re.UNICODE)

# Recherche le pattern d'anime
cartoon_pattern = r"^(?P<title_cartoon>.+?)(?: ~ (?P<subtitle_cartoon>.+?))? - (?P<genre>.+?) - (?P<language>.+?)(?: - (?P<title_music>.+?))?(?: \((?P<detail>.*)\))?$"
cartoon_re = re.compile(cartoon_pattern, re.UNICODE)

# Recherche le pattern d'anime
anime_pattern = r"^(?P<title_anime>.+?)(?: ~ (?P<subtitle_anime>.+?))? - (?P<genre>.+?) - (?P<title_music>.+?)(?: \((?P<detail>.*)\))?$"
anime_re = re.compile(anime_pattern, re.UNICODE)

# Recherche les patterns de genre, dans le désordre, une seule fois
genre_pattern = r"^(?=(?:.*(?:(?P<op>OP(?P<op_nbr>\d*))\b|(?P<ed>ED(?P<ed_nbr>\d*))\b|(?P<ins>INS)\b|(?P<is>IS)\b))?)(?=(?:.*(?:(?P<pv>PV)\b|(?P<amv>AMV)\b|(?P<live>LIVE)\b))?)(?=(?:.*(?:(?P<court>COURT)\b|(?P<long>LONG)\b))?)(?=(?:.*(?P<inst>INST)\b)?)(?=(?:.*(?P<cover>COVER)\b)?)(?=(?:.*(?P<remix>REMIX)\b)?)(?=(?:.*(?P<spoil>SPOIL)\b)?).+"
genre_re = re.compile(genre_pattern, re.UNICODE)


##
# Fonctions
#


def music_file2data(file):
    """ Décompose le nom de fichier en éléments distincts pour une musique

        entrée :
            <unicode> nom du fichier, sans l'extension

        sortie :
            <dict> dictionnaire des infos :
                'composer'    <list> compositeurs
                'singer'      <list> chanteurs
                'genre'       <dict> genre : voir genre_file2data
                'title_music' <unicode> titre musique
                'detail'      <unicode> détail
"""
    match = music_re.match(file)

    if not match:
        print(file)
        raise MusicConventionError("String de la musique non conforme")

    data = match.groupdict('')

    data['composer'] = data['composer'].split(', ')
    data['singer'] = data['singer'].split(', ')
    data['genre'] = genre_file2data(data['genre'])

    if check:
        music_check(data)

    return data


def cartoon_file2data(file):
    """ Décompose le nom de fichier en éléments distincts pour un dessin animé

        entrée :
            <unicode> nom du fichier, sans l'extension

        sortie :
            <dict> dictionnaire des infos :
                'title_cartoon'    <unicode> titre dessin animé
                'subtitle_cartoon' <unicode> sous titre dessin animé
                'genre'            <dict> genre : voir genre_file2data
                'language'         <unicode> langue du dessin animé
                'title_music'      <unicode> titre musique
                'detail'           <unicode> détail
"""
    match = cartoon_re.match(file)

    if not match:
        print(file)
        raise CartoonConventionError("String du dessin animé non conforme")

    data = match.groupdict('')

    data['genre'] = genre_file2data(data['genre'])

    if check:
        cartoon_check(data)

    return data


def anime_file2data(file):
    """ Décompose le nom de fichier en éléments distincts pour un anime

        entrée :
            <unicode> nom du fichier, sans l'extension

        sortie :
            <dict> dictionnaire des infos :
                'title_anime'    <unicode> titre anime
                'subtitle_anime' <unicode> sous titre anime
                'genre'          <dict> genre : voir genre_file2data
                'title_music'    <unicode> titre musique
                'detail'         <unicode> détail
"""
    match = anime_re.match(file)

    if not match:
        print(file)
        raise AnimeConventionError("String de l'anime non conforme")

    data = match.groupdict('')

    data['genre'] = genre_file2data(data['genre'])

    if check:
        anime_check(data)

    return data


def genre_file2data(file):
    """ Décompose le string de genre en dictionnaire de booléens ou d'entiers

        entrée :
            <unicode> string des genres

        sortie :
            <dict> dictionnaire de drapeaux/valeurs :
                'op'     <bool> opening
                'op_nbr' <int> opening #
                'ed'     <bool> ending
                'ed_nbr' <int> ending #
                'ins'    <bool> insert song
                'is'     <bool> image song
                'pv'     <bool> promotionnal video
                'amv'    <bool> anime music video
                'live'   <bool> version live
                'court'  <bool> version courte
                'long'   <bool> version longue
                'inst'   <bool> piste instrumentale disponible
                'cover'  <bool> cover de la version originale
                'remix'  <bool> remix de la musique originale
                'spoil'  <bool> présente du spoil
"""
    match = genre_re.match(file)

    if not match:
        print(file)
        raise GenreConventionError("String du genre non conforme")

    data_raw = match.groupdict(False)
    data = {}
    # tranformation des résultats en booléens, sauf pour le numéro d'opening et
    # d'ending
    for k, d in data_raw.items():
        data[k] = d is not False if k not in ('op_nbr', 'ed_nbr') \
            else int(d) if d else 0

    if check:
        genre_check(data, file)

    return data


def music_data2file(data):
    """ Recompose le nom de fichier depuis les éléments distincts pour une musique

        entrée :
            <dict> dictionnaire des infos :
                'title_anime'    <list> compositeurs
                'subtitle_anime' <list> chanteurs
                'genre'          <dict> genre : voir genre_file2data
                'title_music'    <unicode> titre musique
                'detail'         <unicode> détail

        sortie :
            <unicode> nom du fichier, sans l'extension
"""
    if check:
        music_check(data)

    data['composer'] = ', '.join(data['composer'])
    data['singer'] = ', '.join(data['singer'])
    if type(data['genre']) is not str:
        data['genre'] = genre_data2file(data['genre'])

    music = '{composer}'
    music += ' feat. {singer}' if data['singer'] else ''
    music += ' - {genre} - {title_music}'
    music += ' ({detail})' if data['detail'] else ''
    file = music.format(**data)

    return file


def cartoon_data2file(data):
    """ Recompose le nom de fichier depuis les éléments distincts pour un cartoon

        entrée :
            <dict> dictionnaire des infos :
                'title_cartoon'    <unicode> titre dessin animé
                'subtitle_cartoon' <unicode> sous titre dessin animé
                'genre'            <dict> genre : voir genre_file2data
                'language'         <unicode> langue du dessin animé
                'title_music'      <unicode> titre musique
                'detail'           <unicode> détail

        sortie :
            <unicode> nom du fichier, sans l'extension
"""
    if check:
        cartoon_check(data)

    if type(data['genre']) is not str:
        data['genre'] = genre_data2file(data['genre'])

    cartoon = '{title_cartoon}'
    cartoon += ' ~ {subtitle_cartoon}' if data['subtitle_cartoon'] else ''
    cartoon += ' - {genre} - {language}'
    cartoon += ' - {title_music}' if data['title_music'] else ''
    cartoon += ' ({detail})' if data['detail'] else ''
    file = cartoon.format(**data)

    return file


def anime_data2file(data):
    """ Recompose le nom de fichier depuis les éléments distincts pour un anime

        entrée :
            <dict> dictionnaire des infos :
                'title_anime'    <unicode> titre anime
                'subtitle_anime' <unicode> sous titre anime
                'genre'          <dict> genre : voir genre_file2data
                'title_music'    <unicode> titre musique
                'detail'         <unicode> détail

        sortie :
            <unicode> nom du fichier, sans l'extension
"""
    if check:
        anime_check(data)

    if type(data['genre']) is not str:
        data['genre'] = genre_data2file(data['genre'])

    anime = '{title_anime}'
    anime += ' ~ {subtitle_anime}' if data['subtitle_anime'] else ''
    anime += ' - {genre} - {title_music}'
    anime += ' ({detail})' if data['detail'] else ''
    file = anime.format(**data)

    return file


def genre_data2file(data, zeros = 0):
    """ Recompose le string de genre depuis le dictionnaire de booléens et d'entiers

        entrée :
            <dict> dictionnaire de drapeaux/valeurs :
                'op'     <bool> opening
                'op_nbr' <int> opening #
                'ed'     <bool> ending
                'ed_nbr' <int> ending #
                'ins'    <bool> insert song
                'is'     <bool> image song
                'pv'     <bool> promotionnal video
                'amv'    <bool> anime music video
                'live'   <bool> version live
                'court'  <bool> version courte
                'long'   <bool> version longue
                'inst'   <bool> piste instrumentale disponible
                'cover'  <bool> cover de la version originale
                'remix'  <bool> remix de la musique originale
                'spoil'  <bool> présente du spoil
            <zeros> ajout artificiel de 0 au numéro d'OP et d'ED

        sortie :
            <unicode> string des genres
"""
    if check:
        genre_check(data)

    if zeros:
        zeros_str = '{0:0{1}n}'.format(0, zeros)
    else:
        zeros_str = ''

    genre = []
    if data['op']:
        op = 'OP'
        op += zeros_str + str(data['op_nbr']) if data['op_nbr'] else ''
        genre.append(op)
    if data['ed']:
        ed = 'ED'
        ed += zeros_str + str(data['ed_nbr']) if data['ed_nbr'] else ''
        genre.append(ed)
    if data['ins']:
        genre.append('INS')
    if data['is']:
        genre.append('IS')
    if data['pv']:
        genre.append('PV')
    if data['amv']:
        genre.append('AMV')
    if data['live']:
        genre.append('LIVE')
    if data['court']:
        genre.append('COURT')
    if data['long']:
        genre.append('LONG')
    if data['inst']:
        genre.append('INST')
    if data['cover']:
        genre.append('COVER')
    if data['remix']:
        genre.append('REMIX')
    if data['spoil']:
        genre.append('SPOIL')
    file = ' '.join(genre)

    return file


##
# Classes d'erreurs
#


class ConventionError(Exception):
    """ Classe pour les erreurs de convention
    """


class MusicConventionError(ConventionError):
    """ Classe pour les erreurs de convention de musique
    """


class AnimeConventionError(ConventionError):
    """ Classe pour les erreurs de convention d'anime
    """


class CartoonConventionError(ConventionError):
    """ Classe pour les erreurs de convention de dessin animé
    """


class GenreConventionError(ConventionError):
    """ Classe pour les erreurs de convention de genre
    """


def music_check(data):
    """ Vérifier la musique
    """
    if type(data['composer']) is not list:
        raise MusicConventionError("Champ des compositeurs non conforme")
    if len(data['composer'][0].strip()) != len(data['composer'][0]):
        raise MusicConventionError(
            "Espaces en trop dans le champ du compositeur")
    if len(data['composer']) > 1:
        composer = list(data['composer'])
        composer.sort(key = lambda e: e.lower())
        if not composer == data['composer']:
            raise MusicConventionError(
                "Compositeurs non rangés dans l'ordre alphabétique")
    if type(data['singer']) is not list:
        raise MusicConventionError("Champ des chanteurs non conforme")
    if not data['singer']:
        raise MusicConventionError("Chanteur absent")
    if not data['singer'][0].strip():
        raise MusicConventionError("Chanteur absent ou non conforme")
    if len(data['singer']) > 1:
        singer = list(data['singer'])
        singer.sort(key = lambda e: e.lower())
        if not singer == data['singer']:
            raise MusicConventionError(
                "Chanteurs non rangés dans l'ordre alphabétique")
    if not data['title_music'].strip():
        raise MusicConventionError("Titre de musique absent ou non conforme")


def cartoon_check(data):
    """ Vérifie le dessin animé
    """
    if not data['title_cartoon'].strip():
        raise CartoonConventionError(
            "Titre de dessin animé absent ou non conforme")
    if not data['language'].strip():
        raise CartoonConventionError("Langue du dessin animé absente")
    if len(data['language']) != 2:
        raise CartoonConventionError(
            "Langue du dessin animé non conforme (2 caractères uniquement)")


def anime_check(data):
    """ Vérifie l'anime
    """
    if not data['title_anime'].strip():
        raise AnimeConventionError("Titre d'anime absent ou non conforme")
    if not data['title_music'].strip():
        raise AnimeConventionError("Titre de musique absent ou non conforme")


def genre_check(data, file = None):
    """ Vérifie les genres
    """
    if not any(data.values()):
        raise GenreConventionError("Genre absent ou non conforme")
    if data['op_nbr'] and not data['op']:
        raise GenreConventionError(
            "Flag OP manquant alors qu'il y a un numéro d'OP")
    if data['ed_nbr'] and not data['ed']:
        raise GenreConventionError(
            "Flag ED manquant alors qu'il y a un numéro d'ED")
    if file is not None:
        if data['op'] and data['op_nbr'] or data['ed'] and data['ed_nbr']:
            error = True
            for i in range(3):
                genre_str = genre_data2file(data, i)
                error *= len(genre_str) == len(file)
            if error:
                print(file)
                raise GenreConventionError("Genre incorrect")
        else:
            genre_str = genre_data2file(data)
            if len(genre_str) != len(file):
                print(file)
                raise GenreConventionError("Genre incorrect")


##
# Show mode
#


if __name__ == "__main__":
    def music_show(input):
        for i in input:
            print(i)
            data = music_file2data(i)
            print(data)
            file = music_data2file(data)
            print(file)

    def anime_show(input):
        for i in input:
            print(i)
            data = anime_file2data(i)
            print(data)
            file = anime_data2file(data)
            print(file)

    music_list = (
        'DECO 27 - PV INST - Mozaic Role',
        'DECO 27 feat. Gumi - PV INST - Mozaic Role',
        'DECO 27 - PV INST - Mozaic Role (Heavy metal version)',
        'DECO 27 feat. Gumi - PV INST - Mozaic Role (Heavy metal version)',
    )

    anime_list = (
        'Girls und Panzer - OP1 - DreamRiser',
        'Girls und Panzer ~ Girls und Panzers Projekt - OP1 - DreamRiser',
        'Girls und Panzer - OP1 - DreamRiser (Special Oharai college version)',
        'Girls und Panzer ~ Girls und Panzers Projekt - OP1 - DreamRiser (\
        Special Oharai college version)',
    )

    print("Musique")
    music_show(music_list)

    print("Anime")
    anime_show(anime_list)
