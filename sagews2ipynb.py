#!/usr/bin/env python
# encoding: utf-8
###############################################################################
# sagews2ipynb Convert a SageMathCloud worksheet into an iPython notebook.
# This is useful because iPython notebooks are the only format
# that works both for pushing/pulling files from sagemathcloud.
#
# Mostly a small modification of sagews2pdf.py by William Stein.
#
# Original copyright follows:
#
# SageMathCloud: A collaborative web-based interface to Sage, IPython, LaTeX and the Terminal.
#
#    Copyright (C) 2014, William Stein
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################



"""
This is a modified sagews2pdf.py so that it outputs an iPython notebook. 

Original copyright follows.


Copyright (c) 2014, William Stein
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

CONTRIBUTORS:

  - William Stein (maintainer and initial author)
  - Cedric Sodhi  - internationalization and bug fixes
  - Tomas Kalvoda - internationalization

"""

MARKERS = {'cell':u"\uFE20", 'output':u"\uFE21"}

# TODO: this needs to use salvus.project_info() or an environment variable or something!
site = 'https://cloud.sagemath.com'

import argparse, base64, cPickle, json, os, shutil, sys, textwrap, HTMLParser, tempfile, urllib
from uuid import uuid4

def escape_path(s):
    # see http://stackoverflow.com/questions/946170/equivalent-javascript-functions-for-pythons-urllib-quote-and-urllib-unquote
    s = urllib.quote(unicode(s).encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')
    return s.replace('#','%23').replace("?",'%3F')

def wrap(s, c=90):
    return '\n'.join(['\n'.join(textwrap.wrap(x, c)) for x in s.splitlines()])

def tex_escape(s):
    return s.replace( "\\","{\\textbackslash}" ).replace( "_","\\_" ).replace( "{\\textbackslash}$","\\$" ).replace('%','\\%').replace('#','\\#').replace("&","\\&")


# Parallel computing can be useful for IO bound tasks.
def thread_map(callable, inputs):
    """
    Computing [callable(args) for args in inputs]
    in parallel using len(inputs) separate *threads*.

    If an exception is raised by any thread, a RuntimeError exception
    is instead raised.
    """
    print "Doing the following in parallel:\n%s"%('\n'.join(inputs))
    from threading import Thread
    class F(Thread):
        def __init__(self, x):
            self._x = x
            Thread.__init__(self)
            self.start()
        def run(self):
            try:
                self.result = callable(self._x)
                self.fail = False
            except Exception, msg:
                self.result = msg
                self.fail = True
    results = [F(x) for x in inputs]
    for f in results: f.join()
    e = [f.result for f in results if f.fail]
    if e: raise RuntimeError(e)
    return [f.result for f in results]


# create a subclass and override the handler methods

class Parser(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.result += '\\section{'
        elif tag == 'h2':
            self.result += '\\subsection{'
        elif tag == 'h3':
            self.result += '\\subsubsection{'
        elif tag == 'i':
            self.result += '\\textemph{'
        elif tag == 'div':
            self.result += '\n\n{'
        elif tag == 'ul':
            self.result += '\\begin{itemize}'
        elif tag == 'ol':
            self.result += '\\begin{enumerate}'
        elif tag == 'hr':
            self.result += '\n\n' + '-'*80 + '\n\n'  #TODO
        elif tag == 'li':
            self.result += '\\item{'
        elif tag == 'a':
            self.result += '\\url{'
        else:
            self.result += '{'  # fallback

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.result += '\\end{itemize}'
        elif tag == 'ol':
            self.result += '\\end{enumerate}'
        elif tag == 'hr':
            self.result += ''
        else:
            self.result += '}'  # fallback

    def handle_data(self, data):
        # safe because all math stuff has already been escaped.
        self.result += tex_escape(data)

def sanitize_math_input(s):
    from markdown2Mathjax import sanitizeInput
    # it's critical that $$ be first!
    delims = [('$$','$$'), ('\\(','\\)'), ('\\[','\\]'),
              ('\\begin{equation}', '\\end{equation}'), ('\\begin{equation*}', '\\end{equation*}'),
              ('\\begin{align}', '\\end{align}'), ('\\begin{align*}', '\\end{align*}'),
              ('\\begin{eqnarray}', '\\end{eqnarray}'), ('\\begin{eqnarray*}', '\\end{eqnarray*}'),
              ('\\begin{math}', '\\end{math}'),
              ('\\begin{displaymath}', '\\end{displaymath}')
              ]

    tmp = [((s,None),None)]
    for d in delims:
        tmp.append((sanitizeInput(tmp[-1][0][0], equation_delims=d), d))

    return tmp

def reconstruct_math(s, tmp):
    from markdown2Mathjax import reconstructMath
    while len(tmp) > 1:
        s = reconstructMath(s, tmp[-1][0][1], equation_delims=tmp[-1][1])
        del tmp[-1]
    return s

def html2tex(doc):
    tmp = sanitize_math_input(doc)
    parser = Parser()
    parser.result = ''
    # The number of (unescaped) dollars or double-dollars found so far. An even
    # number is assumed to indicate that we're outside of math and thus need to
    # escape.
    parser.dollars_found = 0
    parser.feed(tmp[-1][0][0])
    return reconstruct_math(parser.result, tmp)


def md2html(s):
    from markdown2 import markdown
    extras = ['code-friendly', 'footnotes', 'smarty-pants', 'wiki-tables', 'fenced-code-blocks']

    tmp = sanitize_math_input(s)
    markedDownText = markdown(tmp[-1][0][0], extras=extras)
    return reconstruct_math(markedDownText, tmp)

def md2tex(doc):
    return html2tex(md2html(doc))

class Cell(object):
    def __init__(self, s):
        self.raw = s
        v = s.split('\n' + MARKERS['output'])
        if len(v) > 0:
            w = v[0].split(MARKERS['cell']+'\n')
            n = w[0].lstrip(MARKERS['cell'])
            self.input_uuid = n[:36]
            self.input_codes = n[36:]
            if len(w) > 1:
                self.input = w[1]
            else:
                self.input = ''
        else:
            self.input_uuid = self.input = ''
        if len(v) > 1:
            w = v[1].split(MARKERS['output'])
            self.output_uuid = w[0] if len(w) > 0 else ''
            self.output = []
            for x in w[1:]:
                if x:
                    try:
                        self.output.append(json.loads(x))
                    except ValueError:
                        try:
                            print "**WARNING:** Unable to de-json '%s'"%x
                        except:
                            print "Unable to de-json some output"
        else:
            self.output = self.output_uuid = ''


    def dict_list(self):
        """
        Returns a list(dict) representation of this cell, along with a list of commands
        that should be executed in the shell in order to obtain remote data files,
        etc., to render this cell.
        """
        self._commands = []
        self._json=[]
        self.serialize_input()
        self.serialize_output()
        return self._json
        # append(self.latex_output()), self._commands

    def serialize_input(self):
        """Return a dict representation of self."""
        d = {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {
                    'collapsed': False,
                    # 'autoscroll': 'auto'
                },
                'source': [self.input.strip()],
                'outputs': []
            }
        if 'i' in self.input_codes:   # hide input
            # d['metadata']['collapsed'] = True
            # skip
            return {}
            
        self._json.append(d)
        

    def serialize_output(self):
        if 'o' in self.input_codes:  # hide output
            return None
        for x in self.output:
            if 'stdout' in x:
                d = {
                    'output_type': 'stream',
                    'name': 'stdout',
                    'text': [wrap(x['stdout'])]
                }
                self._json[0]['outputs'].append(d)
            if 'stderr' in x:
                d = {
                    'output_type': 'stream',
                    'name': 'stderr',
                    'text': [wrap(x['stderr'])]
                }
                self._json[0]['outputs'].append(d)
            if 'code' in x:
                # TODO: for now ignoring that not all code is Python...
                # s += "\\begin{lstlisting}" + x['code']['source'] + "\\end{lstlisting}"
                # Should this be in a cell by itself?
                d = {
                    'output_type': 'stream',
                    'name': 'stdout',
                    'text': [wrap(x['code']['source'])]
                }
                self._json[0]['outputs'].append(d)
            if 'html' in x:
                # s += html2tex(x['html'])
                d = {
                    'output_type': 'execute_result',
                    'data': {
                        'text/html': [x['html']]
                    },
                    'metadata': {},
                    'execution_count': None
                }
                self._json[0]['outputs'].append(d)
            if 'md' in x:
                # s += md2tex(x['md'])
                d={
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': x['md']
                }
                # Overwrite the original cell:
                self._json=[d]
                
            if 'interact' in x:
                pass
            if 'tex' in x:
                val = x['tex']
                # if 'display' in val:
                #     s += "$$%s$$"%val['tex']
                # else:
                #     s += "$%s$"%val['tex']
                s="$$%s$$"%val['tex'] if 'display' in val else "$%s$"%val['tex']
                d = {
                    'output_type': 'execute_result',
                    'data': {
                        'text/latex': [s]
                    },
                    'execution_count': None,
                    'metadata': {}
                }
            if 'file' in x:                
                pass
                val = x['file']
                if 'url' in val:
                    target = val['url']
                    filename = os.path.split(target)[-1]
                else:
                    filename = os.path.split(val['filename'])[-1]
                    target = "%s/blobs/%s?uuid=%s"%(site, escape_path(filename), val['uuid'])
                
                print (target, filename)

                base, ext = os.path.splitext(filename)
                ext = ext.lower()[1:]
                # if ext in ['jpg', 'png', 'eps', 'pdf', 'svg']:
                #     img = ''
                #     i = target.find("/raw/")
                #     if i != -1:
                #         src = os.path.join(os.environ['HOME'], target[i+5:])
                #         if os.path.abspath(src) != os.path.abspath(filename):
                #             try:
                #                 shutil.copyfile(src, filename)
                #             except Exception, msg:
                #                 print msg
                #         img = filename
                #     else:
                #         # Get the file from remote server
                #         c = 'rm -f "%s"; wget "%s" --output-document="%s"'%(filename, target, filename)
                #         # If we succeeded, convert it to a png, which is what we can easily embed
                #         # in a latex document (svg's don't work...)
                #         self._commands.append(c)
                #         if ext == 'svg':
                #             # hack for svg files; in perfect world someday might do something with vector graphics, see http://tex.stackexchange.com/questions/2099/how-to-include-svg-diagrams-in-latex
                #             # Now we live in a perfect world, and proudly introduce inkscape as a dependency for SMC :-)
                #             #c += ' && rm -f "%s"; convert -antialias -density 150 "%s" "%s"'%(base+'.png',filename,base+'.png')
                #             # converts the svg file into pdf
                #             c += ' && rm -f "%s"; inkscape --without-gui --export-pdf=%s "%s"'%(base+'.pdf',base+'.pdf',filename)
                #             self._commands.append(c)
                #             filename = base+'.pdf'
                #         img = filename
                #     s += '\\includegraphics[width=\\textwidth]{%s}\n'%img
                # elif ext == 'sage3d' and 'sage3d' in extra_data and 'uuid' in val:
                #     # render a static image, if available
                #     v = extra_data['sage3d']
                #     print "KEYS", v.keys()
                #     uuid = val['uuid']
                #     if uuid in v:
                #         print "TARGET acquired!"
                #         data = v[uuid].pop()
                #         width = min(1, 1.2*data.get('width',0.5))
                #         print "width = ", width
                #         if 'data-url' in data:
                #             data_url = data['data-url']  # 'data:image/png;base64,iVBOR...'
                #             i = data_url.find('/')
                #             j = data_url.find(";")
                #             k = data_url.find(',')
                #             image_ext  = data_url[i+1:j]
                #             image_data = data_url[k+1:]
                #             assert data_url[j+1:k] == 'base64'
                #             filename = str(uuid4()) + "." + image_ext
                #             open(filename, 'w').write(base64.b64decode(image_data))
                #             s += '\\includegraphics[width=%s\\textwidth]{%s}\n'%(width, filename)
                #
                # else:
                #     if target.startswith('http'):
                #         s += '\\url{%s}'%target
                #     else:
                #         s += '\\begin{verbatim}['+target+']\\end{verbatim}'
                #
        # return s



class Worksheet(object):
    def __init__(self, filename=None, s=None):
        """
        The worksheet defined by the given filename or UTF unicode string s.
        """
        self._default_title = ''
        if filename:
            self._filename = os.path.abspath(filename)
        else:
            self._filename = None
        if filename is not None:
            self._default_title = filename
            self._init_from(open(filename).read().decode('utf8'))
        elif s is not None:
            self._init_from(s)
        else:
            raise ValueError("filename or s must be defined")

    def _init_from(self, s):
        self._cells = [Cell(x) for x in s.split('\n'+MARKERS['cell'])]

    def __getitem__(self, i):
        return self._cells[i]

    def __len__(self):
        return len(self._cells)
        
    def json(self, filename, title, author, date):
        dlist=[]
        for C in self._cells:
            dlist += C.dict_list()
        d={
            'nbformat': 4,
            'nbformat_minor': 0,
            'cells': dlist,
            'metadata': {
                'filename': filename,
                'title': title,
                'author': author,
                'date': date
            },
        }
        return json.dumps(d)

def sagews_to_json(filename, title='', author='', date='', outfile='', contents=True, remove_tmpdir=True):
    base = os.path.splitext(filename)[0]
    if not outfile:
        nb = base + ".ipynb"
    else:
        nb = outfile
    print "converting: %s --> %s"%(filename, nb)
    W = Worksheet(filename)
    s=W.json(filename, title, author, date)
    open(nb,'w').write(s.encode('utf8'))
    

# def sagews_to_pdf(filename, title='', author='', date='', outfile='', contents=True, remove_tmpdir=True):
#     base = os.path.splitext(filename)[0]
#     if not outfile:
#         pdf = base + ".pdf"
#     else:
#         pdf = outfile
#     print "converting: %s --> %s"%(filename, pdf)
#     W = Worksheet(filename)
#     temp = ''
#     try:
#         temp = tempfile.mkdtemp()
#         if not remove_tmpdir:
#             print "Temporary directory retained: %s" % temp
#         cur = os.path.abspath('.')
#         os.chdir(temp)
#         open('tmp.tex','w').write(W.latex(title=title, author=author, date=date, contents=contents).encode('utf8'))
#         os.system('pdflatex -interact=nonstopmode tmp.tex')
#         if contents:
#             os.system('pdflatex -interact=nonstopmode tmp.tex')
#         if os.path.exists('tmp.pdf'):
#             shutil.move('tmp.pdf',os.path.join(cur, pdf))
#             print "Created", os.path.join(cur, pdf)
#     finally:
#         if temp and remove_tmpdir:
#             shutil.rmtree(temp)
#         else:
#             print "Leaving latex files in '%s'"%temp

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="convert a sagews worksheet to a pdf file via latex")
    parser.add_argument("filename", help="name of sagews file (required)", type=str)
    parser.add_argument("--author", dest="author", help="author name for printout", type=str, default="")
    parser.add_argument("--title", dest="title", help="title for printout", type=str, default="")
    parser.add_argument("--date", dest="date", help="date for printout", type=str, default="")
    parser.add_argument("--contents", dest="contents", help="include a table of contents 'true' or 'false' (default: 'true')", type=str, default='true')
    parser.add_argument("--outfile", dest="outfile", help="output filename (defaults to input file with sagews replaced by pdf)", type=str, default="")
    parser.add_argument("--remove_tmpdir", dest="remove_tmpdir", help="if 'false' do not delete the temporary LaTeX files and print name of temporary directory (default: 'true')", type=str, default='true')
    parser.add_argument("--extra_data_file", dest="extra_data_file", help="JSON format file that contains extra data useful in printing this worksheet, e.g., 3d plots", type=str, default='')

    args = parser.parse_args()
    args.contents = args.contents == 'true'
    args.remove_tmpdir = args.remove_tmpdir == 'true'

    if args.extra_data_file:
        import json
        extra_data = json.loads(open(args.extra_data_file).read())
    else:
        extra_data = {}

    sagews_to_json(args.filename, title=args.title.decode('utf8'),
                  author=args.author.decode('utf8'), outfile=args.outfile,
                  date=args.date, contents=args.contents, remove_tmpdir=args.remove_tmpdir)
