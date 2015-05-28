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
import StringIO

def escape_path(s):
    # see http://stackoverflow.com/questions/946170/equivalent-javascript-functions-for-pythons-urllib-quote-and-urllib-unquote
    s = urllib.quote(unicode(s).encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')
    return s.replace('#','%23').replace("?",'%3F')

def wrap(s, c=90):
    return '\n'.join(['\n'.join(textwrap.wrap(x, c)) for x in s.splitlines()])

def tex_escape(s):
    return s.replace( "\\","{\\textbackslash}" ).replace( "_","\\_" ).replace( "{\\textbackslash}$","\\$" ).replace('%','\\%').replace('#','\\#').replace("&","\\&")

## Removed lots of code here.

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
                # 'metadata': {
                #     'collapsed': False,
                #     # 'autoscroll': 'auto'
                # },
                'metadata': {},
                'source': [self.input.strip()],
                'outputs': []
            }
        if 'i' in self.input_codes:   # hide input
            # d['metadata']['collapsed'] = True
            # if it's hidden, skip it.
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
                self._json[0]['outputs'].append(d)
                
            if 'file' in x:                
                val = x['file']
                #
                if 'url' in val:
                    target = val['url']
                    filename = os.path.split(target)[-1]
                else:
                    filename = os.path.split(val['filename'])[-1]
                    target = "%s/blobs/%s?uuid=%s"%(site, escape_path(filename), val['uuid'])
                    
                try:
                    file_content=StringIO.StringIO(urllib.urlopen(target).read())
                except:
                    print "Could not read %s, skipping."%target
                    return
                    
                base, ext = os.path.splitext(filename)
                ext = ext.lower()[1:]
                if ext in ['svg']:
                    d = {
                        'output_type': 'execute_result',
                        'execution_count': None,
                        'metadata': {},
                        'data': {
                            "image/svg+xml": [file_content.getvalue()],
                            'text/plain': ["<SVG Object>\n"]
                        }
                    }
                    # print "holita"
                    self._json[0]['outputs'].append(d)
                elif ext in ['jpg', 'png', 'eps', 'pdf']:
                    d = {
                        'output_type': 'execute_result',
                        'execution_count': None,
                        'metadata': {},
                        'data': {
                            'image/'+ext: [base64.b64encode(file_content.getvalue())]
                        }
                    }
                    self._json[0]['outputs'].append(d)
                else:
                    print "Skipping (%s: %s)"%(filename, target)
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
        return json.dumps(d, indent=4)

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
