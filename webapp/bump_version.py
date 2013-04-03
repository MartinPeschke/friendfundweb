#!/usr/bin/env python
import os, re
import re
import subprocess
import logging
import optparse

REV_IDENT = re.compile("^SVNREVISION.*")
SETUP_REV_IDENT = re.compile("""^(?P<start>\W*version=["'])[^"']+(?P<end>["'],)$""")

def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-r", "--revision", dest="revision",
                    action="store",
                    help="revision to bump to")
    options, args = parser.parse_args()

    if not options.revision:
        parser.error('Must add -r argument')
    
    inf = open('./friendfund/lib/app_globals.py', 'r')
    input = inf.readlines()
    output = []
    try:
        for line in input:
            if REV_IDENT.match(line):
                output.append(re.sub(REV_IDENT, 'SVNREVISION="%s"' % options.revision, line))
            else:
                output.append(line)
    finally:
        inf.close()

    outf = open('./friendfund/lib/app_globals.py', 'w')
    try:
        outf.writelines(output)
    finally:
        outf.close()
    
    inf = open('./setup.py', 'r')
    input = inf.readlines()
    output = []
    try:
        for line in input:
            if SETUP_REV_IDENT.match(line):
                output.append(re.sub(SETUP_REV_IDENT, '\g<start>%s\g<end>' % options.revision, line))
            else:
                output.append(line)
    finally:
        inf.close()

    outf = open('./setup.py', 'w')
    try:
        outf.writelines(output)
    finally:
        outf.close()


if __name__ == "__main__":
    main()