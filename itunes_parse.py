from xml.etree import ElementTree as et


# Bad use of context manager, introduces tons of indentation and could be done
# easier with a lambda.  Just playing around for the moment.
class Tag(object):
    def __init__(self, stream, tag):
        self.stream = stream
        self.tag = tag

    def __enter__(self):
        self.stream.write('%s\n' % (self.tag))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            tag_start, tag_end = self.tag.split('<')
        except ValueError:
            # No closing tag?
            tag_start = '<'
            tag_end = '>'

        self.stream.write('\n<%s/%s\n' % (tag_start, tag_end))

    def text(self, text):
        self.stream.write('\t%s' % (text))


def _track_meta(track):
    # Get headers for track meta data like name, album, artist, etc.
    return [t[0].text for t in zip(track[0::2], track[1::2])]


def main():
    # Could use argparse, but keep it simple for now
    import sys
    if len(sys.argv) != 3:
        print 'Usage: <in_file.xml> <out_file.html>'
        sys.exit(1)

    xml = sys.argv[1]
    html = sys.argv[2]

    # FIXME: This uses a lot of memory, maybe we shouldn't read entire file
    # into memory at once?
    root = et.parse(xml).getroot()
    tracks = root.find('dict').find('dict').findall('dict')

    # Don't show all the columns
    name_idx = 1
    end_album_idx = 4

    try:
        headers = [k.text for k in tracks[0].findall('key')[name_idx:end_album_idx]]
    except IndexError:
        headers = []

    html_file = open(html, 'w')
    html_file.write('<!doctype html>')

    with Tag(html_file, '<html>'):
        with Tag(html_file, '<head>'):
            html_file.write('<meta charset="utf-8">')
            html_file.write('<link rel="stylesheet" type="text/css" ' + (
                             'href="bootstrap/css/bootstrap.min.css">'))

            with Tag(html_file, '<title>'):
                html_file.write('iTunes Library')

        with Tag(html_file, '<table class="table table-striped">'):
            with Tag(html_file, '<tr>') as tr:
                for header in headers:
                    with Tag(html_file, '<th>') as th:
                        th.text(header)

            # Sort by artist then album
            for track in sorted(tracks, key=lambda t: (t[5].text, t[7].text)):
                # Skip tracks that have missing name, album or artist will be
                # skipped
                meta = _track_meta(track)
                if 'Name' not in meta or 'Album' not in meta or (
                   'Artist' not in meta):
                    continue

                with Tag(html_file, '<tr>') as tr:
                    for item in track[3:8:2]:
                        with Tag(html_file, '<td>') as td:
                            try:
                                td.text('%s' % (item.text))
                            except UnicodeEncodeError:
                                td.text('&nbsp;')

    html_file.close()

if __name__ == "__main__":
    main()
