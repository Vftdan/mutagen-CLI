#! /usr/bin/env python3

from mutagen import File
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import TPE1, TALB, TIT2, WORS, TDRL, APIC, TRCK
import argparse
import re
import os


def main():
    parser = argparse.ArgumentParser(
        'Change or manipulate the ID3 tags of the audio files')
    parser.add_argument('--track', '-n', type=int, default=None,
                        help='set the track number')
    parser.add_argument('--track-total', '-N', type=int, default=None,
                        help='set total number of tracks')
    parser.add_argument('--artist', '-a', default=None,
                        help='set the artist name')
    parser.add_argument('--album', '-A', default=None,
                        help='set the album name')
    parser.add_argument('--title', '-t', default=None,
                        help='set the title name')
    parser.add_argument('--wors', '-r', default=None,
                        help='set the internet radio url')
    parser.add_argument('--year', '-Y', default=None,
                        help='set the release year')
    parser.add_argument('--cover', '-c', default=None,
                        help='set the cover image')
    parser.add_argument('--format', '-f', default=None,
                        help='return the ID3 information as a formatted'
                        '''string;
                           the format string should containing one or more'''
                        ''' of the following specifiers:
                           , {track}
                           , {artist}
                           , {title}
                           , {album}
                           , {year}
                           , {kbps}
                           , {wors}
                           , {len} (the length of the audio file, in seconds)
                           , {path} (the absolute path of the file)''')
    parser.add_argument('--separator', '-s', default='\n',
                        help='define the separator used to append at the end'
                        ' of the output for each file (excluding the last'
                        ' file)')
    parser.add_argument('--escape', '-e', default='',
                        help='define the characters that should be escaped in'
                        ' all the outputed fields')
    parser.add_argument('audiofile', nargs='+',
                        help='an audio file containing the ID3 tags')

    args = parser.parse_args()

    # input section
    to_track = args.track
    to_track_total = args.track_total
    to_artist = args.artist
    to_album = args.album
    to_title = args.title
    to_wors = args.wors
    to_year = args.year
    to_cover = args.cover
    if to_cover is not None:
        cover_ext = os.path.splitext(to_cover)[1]
        # print("Cover path is "+to_cover)
        import mimetypes
        mimetypes.init()
        to_cover_mime = mimetypes.types_map[cover_ext]
        # print("Mime type is "+to_cover_mime)

    # output section
    outputs = []
    formatstr = args.format
    escapepat = ""
    delimiter = ''
    for c in args.escape:
        esc = ''
        if c in r'()[]\^$.|?*+{}':
            esc = '\\'
        escapepat = escapepat + delimiter + esc + c
        delimiter = '|'
    to_escape = False
    if escapepat != '':
        to_escape = True
        escapepat = '(%s)' % escapepat
    separator = args.separator

    def getinfo(file_):
        try:
            return (file_.info.bitrate / 1000, int(round(file_.info.length)))
        except:
            return (0, 0)

    for f in args.audiofile:
        path = os.path.realpath(f)
        artist = title = album = year = wors = ""
        file_ = File(f)
        kbps, len_ = getinfo(file_)
        try:
            if (type(file_) == MP3):
                # add ID3 tag if it doesn't exist
                try:
                    file_.add_tags()
                except:
                    pass
                # should we set the tag in anyway?
                if to_track is not None or to_track_total is not None:
                    old = (0, 0)
                    if 'TRCK' in file_:
                        try:
                            old = tuple(map(int, file_['TRCK'].text[0]
                                            .split('/')))
                            old = (old + (0, 0))[:2]
                        except:
                            pass
                    if to_track is None:
                        to_track = old[0]
                    if to_track_total is None:
                        to_track_total = old[1]
                    file_['TRCK'] = TRCK(encoding=3, text='%02d' % to_track +
                                         ' / %02d' % to_track_total
                                         if to_track_total else '')
                    if to_track == 0 and to_track_total == 0:
                        del file_['TRCK']
                if to_artist is not None:
                    file_['TPE1'] = TPE1(encoding=3, text=to_artist)
                if to_album is not None:
                    file_['TALB'] = TALB(encoding=3, text=to_album)
                if to_title is not None:
                    file_['TIT2'] = TIT2(encoding=3, text=to_title)
                if to_wors is not None:
                    file_['WORS'] = WORS(url=to_wors)
                if to_year is not None:
                    file_['TDRL'] = TDRL(encoding=3, text=to_year)
                if to_cover is not None:
                    # print('The image data is '+open(to_cover).read())
                    file_['APIC:'] = APIC(
                        encoding=3,
                        mime=to_cover_mime,
                        type=3,
                        data=open(to_cover).read()
                    )
                file_.save()

                # process mp3 specific tag information
                track = file_['TRCK'].text[0] if 'TRCK' in file_ \
                    else ''
                artist = file_['TPE1'].text[0] if 'TPE1' in file_ \
                    else ''
                album = file_['TALB'].text[0] if 'TALB' in file_ \
                    else ''
                title = file_['TIT2'].text[0] if 'TIT2' in file_ \
                    else ''
                wors = file_['WORS'].url if 'WORS' in file_ else ''
                year = file_['TDRL'].text[0] if 'TDRL' in file_ else ''
            elif (type(file_) == MP4):
                # should we set the tag in anyway?
                if to_track is not None or to_track_total is not None:
                    old = (0, 0)
                    if 'trkn' in file_:
                        try:
                            old = tuple(map(int, file_['trkn'][0]))
                            old = (old + (0, 0))[:2]
                        except:
                            pass
                    if to_track is None:
                        to_track = old[0]
                    if to_track_total is None:
                        to_track_total = old[1]
                    file_['trkn'] = [(to_track, to_track_total)]
                    if to_track == 0 and to_track_total == 0:
                        del file_['trkn']
                if to_artist is not None:
                    file_['\xa9ART'] = [to_artist]
                if to_album is not None:
                    file_['\xa9alb'] = [to_album]
                if to_title is not None:
                    file_['\xa9nam'] = [to_title]
                if to_year is not None:
                    file_['\xa9day'] = [to_year]
                if to_cover is not None:
                    file_['covr'] = [open(to_cover).read()]
                file_.save()

                track = '%02d / %02d' % file_['trkn'][0] if 'trkn' in file_ \
                    else ''
                artist = file_['\xa9ART'][0] if '\xa9ART' in file_ \
                    else ''
                album = file_['\xa9alb'][0] if '\xa9alb' in file_ \
                    else ''
                title = file_['\xa9nam'][0] if '\xa9nam' in file_ \
                    else ''
                year = file_['\xa9day'][0] if '\xa9day' in file_ \
                    else ''
        except:
            pass

        reps = {'track': track,
                'artist': artist,
                'title': title,
                'album': album,
                'year': year,
                "kbps": kbps,
                'wors': wors,
                'len': len_,
                'path': path}
        if to_escape:
            for k in reps:
                reps[k] = re.sub(escapepat, r'\\\1', u"%s" % reps[k])

        if formatstr is not None:
            outputs.append(formatstr.format(**reps))

    output = separator.join(outputs)
    print(output, end='')


if __name__ == '__main__':
    main()
