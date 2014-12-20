# Example of dic based on the CherryPy songs tutorial
# See https://cherrypy.readthedocs.org/en/3.3.0/tutorial/REST.html#getting-started

import cherrypy
import dic


class Song(object):
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

    def __repr__(self):
        return 'title: %s, artist: %s' % (self.title, self.artist)


class SongDatabase(object):
    def __init__(self, song_factory: dic.rel.Factory(Song)):
        self.song_factory = song_factory
        self.songs = {}

    def add_song(self, ident, title, artist):
        self.songs[ident] = self.song_factory(title=title, artist=artist)

    def __getitem__(self, ident):
        return self.songs[ident]

    def __str__(self):
        return self.songs.__str__()


class Songs:
    exposed = True

    def __init__(self, song_database: SongDatabase):
        self.songs = song_database
        self.songs.add_song('1', 'Lumberjack Song', 'Canadian Guard Choir')
        self.songs.add_song('2', 'Always Look On the Bright Side of Life', 'Eric Idle')
        self.songs.add_song('3', 'Spam Spam Spam', 'Monty Python')

    def GET(self, id=None):

        if id is None:
            return('Here are all the songs we have: %s' % self.songs)
        elif id in self.songs:
            song = self.songs[id]

            return(
                'Song with the ID %s is called %s, and the artist is %s' % (
                    id, song.title, song.artist))
        else:
            return('No song with the ID %s :-(' % id)


if __name__ == '__main__':
    builder = dic.container.ContainerBuilder()
    builder.register_class(Songs)
    builder.register_class(SongDatabase)
    builder.register_class(Song)

    container = builder.build()

    cherrypy.tree.mount(
        container.resolve(Songs), '/api/songs',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
         }
    )

    cherrypy.engine.start()
    cherrypy.engine.block()
