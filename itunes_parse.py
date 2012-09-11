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


def main():
    # Could use argparse, but keep it simple for now
    import sys
    if len(sys.argv) != 3:
        print 'Usage: <in_file.xml> <out_file.html'
        sys.exit(1)

    xml = sys.argv[1]
    html = sys.argv[2]

    root = et.parse(xml).getroot()
    tracks = root.find('dict').find('dict').findall('dict')

    try:
        headers = [k.text for k in tracks[0].findall('key')]
    except IndexError:
        headers = []

    html_file = open(html, 'w')
    html_file.write('<!doctype html>')

    with Tag(html_file, '<html>'):
        with Tag(html_file, '<head>'):
            html_file.write('<meta charset="utf-8">')
            with Tag(html_file, '<title>'):
                html_file.write('iTunes Library')

        with Tag(html_file, '<table>'):
            with Tag(html_file, '<tr>') as tr:
                for header in headers:
                    with Tag(html_file, '<th>') as th:
                        th.text(header)

            for track in tracks:
                with Tag(html_file, '<tr>') as tr:
                    for key, val in zip(track[0::2], track[1::2]):
                        with Tag(html_file, '<td>') as td:

                            try:
                                td.text('%s' % (val.text))
                            except UnicodeEncodeError:
                                td.text('&nbsp;')

    html_file.close()

if __name__ == "__main__":
    main()
