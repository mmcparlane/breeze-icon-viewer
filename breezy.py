#    Generates an HTML view of KDE Breeze Icons
#
#    Copyright (C) 2020  Mason McParlane
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
    
import sys
import os
import argparse
import re

class SvgFile:
    def __init__(self, svg):
        self.name = os.path.basename(svg)
        self.path = svg
        self.resolved = os.path.normpath(
            self.resolveFilePath(svg))

        m = re.search(r'(\d+)', self.resolved)
        self.size = m.group(1) if m else 32

    def __str__(self):
        return f'name: "{self.name}", path: "{self.path}", resolved: "{self.resolved}"'
        
    def resolveFilePath(self, svg):
        baseDir = os.path.dirname(svg)
        
        if os.path.islink(svg):
            return os.path.join(baseDir, os.readlink(svg))

        with open(svg) as f:
            alias = os.path.join(baseDir, f.readline().rstrip())
            
            if os.path.isfile(alias):
                return alias

        return svg

    def img(self):
        return f'<img src="{self.resolved}" width="{self.size}" height="{self.size}">'

def writeHtml(svgs, dst):
    newline = "\n"
    divs = []
    for k, v in svgs.items():
        divs.append(f"<div class='group'><span>{k}</span>{newline.join([svg.img() for svg in v])}</div>")
    
    print(f"""
<html>
    <head>
        <style>
            .group {{
                display: inline;
                position: relative;
            }}

            .group span {{
                display: none;
                position: absolute;
                top: 2em;
                z-index: 100;
                background: #333;
                color: #fff;
            }}

            .group:hover span {{
                display: inline;
            }}
        </style>
    </head>
    <body>

{newline.join(divs)}

    </body>
</html>
          """, file=dst)
    
if __name__ == '__main__':
    p = argparse.ArgumentParser(
            description='Generate HTML view of breeze icons')
    p.add_argument('--in', dest='inDir', help='Input icon theme directory')
    p.add_argument('--out', dest='outFile', help='Output HTML file')
    
    args = p.parse_args()

    if not os.path.isdir(args.inDir):
        print(f'"{args.inDir}" is not a directory')
        sys.exit(1)

    svgs = {}
    for root, dirs, files in os.walk(args.inDir):
        for f in files:
            if f.endswith('.svg'):
                svg = SvgFile(os.path.join(root, f))
                
                if svg.name not in svgs:
                    svgs[svg.name] = []
                    
                svgs[svg.name].append(svg)

    if args.outFile:
        with open(args.outFile, 'w') as f:
            writeHtml(svgs, f)
    else:
        writeHtml(svgs, sys.stdout)


