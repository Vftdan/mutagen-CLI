#! /usr/bin/env python3

from mutagen import File
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3, TPE1, TALB, TIT2, WORS, TDRL, APIC
import argparse
import re
import os

def main():
    parser = argparse.ArgumentParser('Change or manipulate the ID3 tags of the audio files')
    parser.add_argument('--artist', '-a', default='',
                        help='set the artist name')
    parser.add_argument('--album', '-A', default='',
                        help='set the album name')
    parser.add_argument('--title', '-t', default='', help='set the title name')
    parser.add_argument('--wors', '-r', default='',
                        help='set the internet radio url')
    parser.add_argument('--year', '-Y', default='',
                        help='set the release year')
    parser.add_argument('--cover', '-c', default='',
                        help='set the cover image')
    parser.add_argument('--format', '-f', default='',
                        help='''return the ID3 information as a formatted string;
                                                        the format string should containing one or more of the following specifiers:
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
    to_artist = args.artist
    to_album = args.album
    to_title = args.title
    to_wors = args.wors
    to_year = args.year
    to_cover = args.cover
    if to_cover != '':
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

    def getinfo(file):
        try:
            return (file.info.bitrate / 1000, int(round(file.info.length)))
        except:
            return (0, 0)

    for f in args.audiofile:
        path = os.path.realpath(f)
        artist = title = album = year = wors = ""
        file = File(f)
        kbps, len = getinfo(file)
        try:
            if (type(file) == MP3):
                # add ID3 tag if it doesn't exist
                try:
                    file.add_tags()
                except:
                    pass
                # should we set the tag in anyway?
                if to_artist != '':
                    file.tags['TPE1'] = TPE1(encoding=3, text=to_artist)
                if to_album != '':
                    file.tags['TALB'] = TALB(encoding=3, text=to_album)
                if to_title != '':
                    file.tags['TIT2'] = TIT2(encoding=3, text=to_title)
                if to_wors != '':
                    file.tags['WORS'] = WORS(url=to_wors)
                if to_year != '':
                    file.tags['TDRL'] = TDRL(encoding=3, text=to_year)
                if to_cover != '':
                    # print('The image data is '+open(to_cover).read())
                    file.tags['APIC:'] = APIC(
                            encoding=3,
                            mime=to_cover_mime,
                            type=3,
                            data=open(to_cover).read()
                    )
                file.save()

                # process mp3 specific tag information
                artist = file.tags['TPE1'].text[0] if 'TPE1' in file.tags \
                    else ''
                album = file.tags['TALB'].text[0] if 'TALB' in file.tags \
                    else ''
                title = file.tags['TIT2'].text[0] if 'TIT2' in file.tags \
                    else ''
                wors = file.tags['WORS'].url if 'WORS' in file.tags else ''
                year = file.tags['TDRL'].text[0] if 'TDRL' in file.tags else ''
            elif (type(file) == MP4):
                # should we set the tag in anyway?
                if to_artist != '':
                    file.tags['\xa9ART'] = [to_artist]
                if to_album != '':
                    file.tags['\xa9alb'] = [to_album]
                if to_title != '':
                    file.tags['\xa9nam'] = [to_title]
                if to_year != '':
                    file.tags['\xa9day'] = [to_year]
                if to_cover != '':
                    file.tags['covr'] = [open(to_cover).read()]
                file.save()

                artist = file.tags['\xa9ART'][0] if '\xa9ART' in file.tags \
                    else ''
                album = file.tags['\xa9alb'][0] if '\xa9alb' in file.tags \
                    else ''
                title = file.tags['\xa9nam'][0] if '\xa9nam' in file.tags \
                    else ''
                year = file.tags['\xa9day'][0] if '\xa9day' in file.tags \
                    else ''
        except:
            pass

        reps = {'artist': artist,
                'title': title,
                'album': album,
                'year': year,
                "kbps": kbps,
                'wors': wors,
                'len': len,
                'path': path}
        if to_escape:
            for k in reps:
                reps[k] = re.sub(escapepat, r'\\\1', u"%s" % reps[k])

        if formatstr != '':
            outputs.append(formatstr.format(**reps))

    output = separator.join(outputs)
    print(output, end='')


if __name__ == '__main__':
    main()
