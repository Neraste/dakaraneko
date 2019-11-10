import logging

from dakara_feeder.song import BaseSong

from karaneko.nekoparse import (
    NekoParseMusic,
    NekoParseTagsMusic,
    NekoParseAnime,
    NekoParseTagsAnime,
    NekoParseCartoon,
    NekoParseTagsCartoon,
    ConventionError,
)


logger = logging.getLogger(__name__)


SUBDIRECTORIES = {
    "cjk_music": "CJKmusic",
    "w_music": "Wmusic",
    "anime": "Anime",
    "live_action": "Live Action",
    "game": "Jeux",
    "cartoon": "Dessins animés",
    "other": "Autre",
}


def default_if_cannot_parse(func):
    """Decorator forcing to return default value if the song cannot be parsed
    """

    def call(self):
        if not self.can_parse:
            return getattr(super(self.__class__, self), func.__name__)()

        return func(self)

    return call


class Song(BaseSong):
    """Class describing a song

    This class is supposed to be overloaded for getting more data from song
    files.

    The main entry point of the class when used by the feeder is the
    `get_representation` method, that will call all the methods to get the song
    data:
        - get_title;
        - get_duration;
        - get_version;
        - get_detail;
        - get_detail_video;
        - get_tags;
        - get_artists;
        - get_works;
        - get_lyrics.

    You should override those methods to suit your needs. See the documentation
    of each method to learn what data format the must return.

    When calling `get_representation`, two special methods are also called for
    performing custom actions, the first one just on entering
    `get_representation`, and the other just befor leaving it:
        - pre_process;
        - post_process.

    You should override those two methods as well. Typically, `pre_process`
    should be overriden to perform preparative actions which result would be
    used by the `get_` methods. On the other hand, `post_process` should be
    overriden to perform final actions on the representation.

    Args.
        base_directory (path.Path): path to the scanned directory.
        paths (directory_lister.SongPaths): paths of the song file.

    Attributes:
        base_directory (path.Path): path to the scanned directory.
        video_path (path.Path): path to the song file, relative to the base
            directory.
        sublitle_path (path.Path): path to the subtitle file, relative to the
            base directory.
        others_path (list of path.Path): list of paths to the other files,
            relative to the base directory.
    """

    def pre_process(self):
        """Process preparative actions

        This method is called at the beginning of `get_representation` and can
        be used to cache data in the instance.
        """
        self.can_parse = True

        # get first relative subdirectory if possible
        if self.video_path.parent:
            self.subdirectory = self.video_path.splitall()[1]

        else:
            self.subdirectory = ""

        # detect which parser to use based on directory
        try:
            if self.subdirectory in (
                SUBDIRECTORIES["cjk_music"],
                SUBDIRECTORIES["w_music"],
            ):
                self.parser = NekoParseMusic(self.video_path.stem)
                self.parser.parse()
                return

            if self.subdirectory in (
                SUBDIRECTORIES["anime"],
                SUBDIRECTORIES["live_action"],
                SUBDIRECTORIES["game"],
            ):
                self.parser = NekoParseAnime(self.video_path.stem)
                self.parser.parse()
                return

            if self.subdirectory in (SUBDIRECTORIES["cartoon"],):
                self.parser = NekoParseCartoon(self.video_path.stem)
                self.parser.parse()
                return

            if self.subdirectory in (SUBDIRECTORIES["other"],):
                self.can_parse = False
                return

        # if error when parsing, mark song as not parsable
        except ConventionError as error:
            logger.warning("Error when parsing file %s: %s", self.video_path, error)
            self.can_parse = False
            return

        # if directory cannot tell which convention to use, try each
        # conventions untill one works
        for parser_class in (NekoParseMusic, NekoParseAnime, NekoParseCartoon):
            try:
                self.parser = parser_class(self.video_path.stem)
                self.parser.parse()
                return

            except ConventionError:
                pass

        # if no conventions seem to apply, mark song as not parsable
        logger.warning("File %s has no detectable convention", self.video_path)
        self.can_parse = False

    def post_process(self, representation):
        """Process final actions

        This method is called at the end of `get_representation` and can be
        used to modify the representation.

        Args:
            representation (dict): JSON-compiliant structure representing the
            song.
        """
        pass

    @default_if_cannot_parse
    def get_title(self):
        """Get the title

        Returns:
            str: Title of the song.
        """
        if isinstance(self.parser, NekoParseCartoon):
            return self.get_title_cartoon()

        return self.parser.title_music

    def get_title_cartoon(self):
        """Get the title for Cartoon convention
        """
        # take cartoon title if music cartoon is not known
        return self.parser.title_music or self.parser.title_cartoon

    @default_if_cannot_parse
    def get_artists(self):
        """Get the list of artists

        Returns:
            list of dict: List of representations of artists. An artist is a
            dictionary containing only one key:
                - name (str): The name of the artist.
        """
        if isinstance(self.parser, NekoParseMusic):
            return self.get_artists_music()

        if isinstance(self.parser, (NekoParseAnime, NekoParseCartoon)):
            return self.get_artists_anime()

    def get_artists_music(self):
        """Get the list of artists for Music convention
        """
        artists = []

        artists.extend(self.parser.singers)
        artists.extend(self.parser.composers)

        if self.parser.extras.original_artist:
            artists.append(self.parser.extras.original_artist)

        return [{"name": artist} for artist in artists]

    def get_artists_anime(self):
        """Get the list of artists for Anime convention
        """
        artists = []

        if self.parser.extras.artist:
            artists.append(self.parser.extras.artist)

        if self.parser.extras.original_artist:
            artists.append(self.parser.extras.original_artist)

        return [{"name": artist} for artist in artists]

    @default_if_cannot_parse
    def get_works(self):
        """Get the list of work links

        Returns:
            list of dict: List of representations of work links. A work link is
            a dictionary containing the following keys:
                - link_type (str): Type of link between the song and the work.
                    Can be either:
                        - "OP", for opening;
                        - "ED", for ending;
                        - "IN", for insert song;
                        - "IS", for image song.
                    You should read the server documentation about those terms;
                - link_type_number (int): For link_type "OP" or "ED", add an
                    ordinal value (e.g. in OP1, OP2);
                - episodes (str): List of episodes where the song is used in
                    the work (e.g. "1, 2, 5");
                - work (dict): Representation of a work, containing the
                    following keys:
                        - title (str): Title of the work;
                        - subtitle (str): Subtitle of the work;
                        - work_type (dict): Representation of the type of a
                            work (e.g. anime), containing the following keys:
                                - query_name (str): Technical name of the type.
                                    To use an existing work type, you should
                                    use only this key;
                                - name (str): Name of the type (not mandatory);
                                - name_plural (str): Plural name of the type
                                    (not mandatory);
                                - icon_name (str): Name of the icon that
                                    represents this work type visually (not
                                    mandatory);
                        - alternative_titles (list of dict): List of
                            representations of alternative titles. An
                            alternative title is a dictionary containing only
                            one key:
                                - title (str): Alternative title of the work.
        """
        if isinstance(self.parser, NekoParseMusic):
            return self.get_works_music()

        if isinstance(self.parser, NekoParseAnime):
            return self.get_works_anime()

        if isinstance(self.parser, NekoParseCartoon):
            return self.get_works_cartoon()

    def get_works_music(self):
        """Get the list of work links for Music convention
        """
        extras = self.parser.extras
        work_link = {"work": {"work_type": {"query_name": "anime"}}}

        if extras.opening:
            work_link["link_type"] = "OP"
            work_link["link_type_number"] = extras.opening_nbr
            work_link["work"]["title"] = extras.opening

        elif extras.ending:
            work_link["link_type"] = "ED"
            work_link["link_type_number"] = extras.ending_nbr
            work_link["work"]["title"] = extras.ending

        elif extras.insert_song:
            work_link["link_type"] = "IN"
            work_link["work"]["title"] = extras.insert_song

        elif extras.image_song:
            work_link["link_type"] = "IS"
            work_link["work"]["title"] = extras.image_song

        # return this work link if it exists
        if work_link.get("link_type"):
            return [work_link]

        # otherwise just return default value
        return super().get_works()

    def get_works_anime(self):
        """Get the list of work links for Anime convention
        """
        work_link = {"work": {"work_type": {}}}

        # specific anime values
        work_link["work"]["title"] = self.parser.title_anime

        if self.parser.subtitle_anime:
            work_link["work"]["subtitle"] = self.parser.subtitle_anime

        if self.subdirectory == SUBDIRECTORIES["anime"]:
            work_link["work"]["work_type"]["query_name"] = "anime"

        elif self.SUBDIRECTORIES == SUBDIRECTORIES["live_action"]:
            work_link["work"]["work_type"]["query_name"] = "live-action"

        elif self.SUBDIRECTORIES == SUBDIRECTORIES["game"]:
            work_link["work"]["work_type"]["query_name"] = "game"

        # comon anime/cartoon values
        self.set_work_anime_cartoon(work_link)

        return [work_link]

    def get_works_cartoon(self):
        """Get the list of work links for Cartoon convention
        """
        work_link = {"work": {"work_type": {"query_name": "cartoon"}}}

        # specific cartoon values
        work_link["work"]["title"] = self.parser.title_cartoon

        if self.parser.subtitle_cartoon:
            work_link["work"]["subtitle"] = self.parser.subtitle_cartoon

        # comon anime/cartoon values
        self.set_work_anime_cartoon(work_link)

        return [work_link]

    def set_work_anime_cartoon(self, work_link):
        """Common function to set work for Anime and Cartoon conventions
        """
        tags = self.parser.tags
        work_link["episodes"] = self.parser.extras.episodes

        if tags.opening:
            work_link["link_type"] = "OP"
            work_link["link_type_number"] = tags.opening_nbr

        elif tags.ending:
            work_link["link_type"] = "ED"
            work_link["link_type_number"] = tags.ending_nbr

        elif tags.insert_song:
            work_link["link_type"] = "IN"

        elif tags.image_song:
            work_link["link_type"] = "IS"

    @default_if_cannot_parse
    def get_tags(self):
        """Get the list of tags

        Returns:
            list of dict: List of representations of tags. A tag is a ditionary
            containing the following keys:
                - name (str): Name of the tag;
                - color_hue (int): Visual hue of the tag (not mandatory);
                - disabled (bool): True if the tag is disabled (not mandatory).
        """
        if isinstance(self.parser, NekoParseMusic):
            return self.get_tags_music()

        if isinstance(self.parser, (NekoParseAnime, NekoParseCartoon)):
            return self.get_tags_anime()

    def get_tags_music(self):
        """Get the list of tags for Music convention
        """
        tags_list = []

        for tag in NekoParseTagsMusic.tags:
            if getattr(self.parser.tags, tag["name"]):
                tags_list.append({"name": tag["serializer"]})

        return tags_list

    def get_tags_anime(self):
        """Get the list of tags for Anime convention
        """
        tags_list = []

        for tag in NekoParseTagsAnime.tags:
            if tag["category"] == "use":
                # ignore use tags
                continue

            if getattr(self.parser.tags, tag["name"]):
                tags_list.append({"name": tag["serializer"]})

        return tags_list

    @default_if_cannot_parse
    def get_version(self):
        """Get the version

        Returns:
            str: Version of the song.
        """
        if isinstance(self.parser, NekoParseCartoon):
            return self.get_version_cartoon()

        return self.parser.extras.version

    def get_version_cartoon(self):
        """Get the version for Cartoon convention
        """
        # concatenate version and language
        return ", ".join(
            value
            for value in (self.parser.extras.version, self.parser.language)
            if value
        )

    @default_if_cannot_parse
    def get_detail(self):
        """Get the datail

        Returns:
            str: Detail about the song.
        """
        return self.parser.details

    @default_if_cannot_parse
    def get_detail_video(self):
        """Get the datail of the video

        Returns:
            str: Detail about the video.
        """
        detail_video_list = []
        if self.parser.extras.video:
            detail_video_list.append(self.parser.extras.video)

        if self.parser.extras.amv:
            detail_video_list.append(self.parser.extras.amv)

        if self.parser.extras.title_video:
            detail_video_list.append(self.parser.extras.title_video)

        return ", ".join(detail_video_list)
