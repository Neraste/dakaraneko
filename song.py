from dakara_feeder.song import BaseSong

from karaneko.nekoparse import (
        NekoParseMusic, NekoParseTagsMusic, ConventionError
        )


def default_if_error(func):
    def call(self):
        if self.parse_error:
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

        This method should be overriden. By default, it does not do anything.

        This method is called at the beginning of `get_representation` and can
        be used to cache data in the instance.
        """
        self.parse_error = False
        if self.video_path.parent:
            directory = self.video_path.splitall()[1]

        else:
            directory = ""

        if directory in ("CJKmusic", "Wmusic"):
            self.parser = NekoParseMusic(self.video_path.stem)
            # TODO

        try:
            self.parser.parse()
        except ConventionError:
            self.parse_error = True

    def post_process(self, representation):
        """Process final actions

        This method should be overriden. By default, it does not do anything.

        This method is called at the end of `get_representation` and can be
        used to modify the representation.

        Args:
            representation (dict): JSON-compiliant structure representing the
            song.
        """
        pass

    @default_if_error
    def get_title(self):
        """Get the title

        This method should be overriden. By default it returns the video file
        name without extension.

        Returns:
            str: Title of the song.
        """
        return self.parser.title_music

    @default_if_error
    def get_artists(self):
        """Get the list of artists

        This method should be overriden. By default it returns an empty list.

        Returns:
            list of dict: List of representations of artists. An artist is a
            dictionary containing only one key:
                - name (str): The name of the artist.
        """
        artists = []
        artists.extend(self.parser.singers)
        artists.extend(self.parser.composers)
        if self.parser.extras.original_artist:
            artists.append(self.parser.extras.original_artist)

        return [{"name": artist} for artist in artists]

    @default_if_error
    def get_works(self):
        """Get the list of work links

        This method should be overriden. By default it returns an empty list.

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
        # Use work information stored in extra details
        extras = self.parser.extras
        work_link = {"work": {"work_type": {"query_name": "anime"}}}

        if extras.opening:
            work_link["link_type"] = "OP"
            work_link["link_type_nb"] = extras.opening_nbr
            work_link["work"]["title"] = extras.opening

        elif extras.ending:
            work_link["link_type"] = "ED"
            work_link["link_type_nb"] = extras.ending_nbr
            work_link["work"]["title"] = extras.ending

        elif extras.insert_song:
            work_link["link_type"] = "IN"
            work_link["work"]["title"] = extras.insert_song

        elif extras.image_song:
            work_link["link_type"] = "IS"
            work_link["work"]["title"] = extras.image_song

        if work_link.get("link_type"):
            return [work_link]

        return []

    @default_if_error
    def get_tags(self):
        """Get the list of tags

        This method should be overriden. By default it returns an empty list.

        Returns:
            list of dict: List of representations of tags. A tag is a ditionary
            containing the following keys:
                - name (str): Name of the tag;
                - color_hue (int): Visual hue of the tag (not mandatory);
                - disabled (bool): True if the tag is disabled (not mandatory).
        """
        tags_list = []

        for tag in NekoParseTagsMusic.tags:
            if getattr(self.parser.tags, tag["name"]):
                tags_list.append({"name": tag["serializer"]})

        return tags_list

    @default_if_error
    def get_version(self):
        """Get the version

        This method should be overriden. By default it returns an empty string.

        Returns:
            str: Version of the song.
        """
        return self.parser.extras.version

    @default_if_error
    def get_detail(self):
        """Get the datail

        This method should be overriden. By default it returns an empty string.

        Returns:
            str: Detail about the song.
        """
        return self.parser.details

    @default_if_error
    def get_detail_video(self):
        """Get the datail of the video

        This method should be overriden. By default it returns an empty string.

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
