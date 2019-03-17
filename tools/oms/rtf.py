# ---------------------------------------------------------------------------
#
# rtf.py, an rtf conversion module for the OpenManuscript toolset 
#
# ---------------------------------------------------------------------------

"""
Copyright (c) 2016-2019, David H. Rogers 
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
"""

from . import core

import json
import os
import re
import datetime


# ---------------------------------------------------------------------------
# global variables
# ---------------------------------------------------------------------------
APP = {
    "name"      : "oms2rtf",
    "version"   : "1.0",
    "sed"       : "sed"
}

#
# current state
#   listnum - current number for numbered lists
#
CURSTATE = {
    "listnum"  : 0,
    "numwords" : 0
}

FONT = {
    "size"    : "24",
    "family"  : "Courier",
    "tableid" : "0"
}

MARGIN = {
    "t" : "1440",
    "b" : "1440",
    "l" : "1440",
    "r" : "1440"
}

SPACING = {
    "paragraph" : "480",
    "parindent" : "720",
    "newchapb"  : "3600",
    "newchapa"  : "360",
    "chapsuba"  : "720",
    "titleskip" : "3600",
    "synopsisb" : "720",
    "synopsisa" : "720",
    "quoteb"    : "1440",
    "quotea"    : "720",
}

# -----------------------------------------------------------------------------
# write document preamble
# -----------------------------------------------------------------------------
def write_preamble( f ):
    notes = "ftnbj"

    f.write("""{{\\rtf1 \\ansi {{\\fonttbl {{\\f0 \\fmodern {0};}}{{\\f1 \\froman Times;}}}}
\\deflang1033 \\plain \\fs{1} \\widowctrl \\hyphauto \\{2}
\\titlepg \\margt{3} \\margb{4} \\margl{5} \\margr{6} \\pgnrestart \\pgnstarts0
\n""".format(FONT["family"], FONT["size"], notes, MARGIN["t"], MARGIN["b"], MARGIN["l"], MARGIN["r"]))

# -----------------------------------------------------------------------------
# write document metadata 
# -----------------------------------------------------------------------------
def write_docinfo( f, author, ms ):
    global APP
    now = datetime.datetime.now()

    f.write("""{{\\info
{{\\title {0}}}
{{\\author {1} {2}}}
{{\\creatim\yr{3}\\mo{4}\\dy{5}\\hr{6}\\min{7}}}
{{\\doccomm Created from OpenManuscript using {8} v{9}}}
}}\n""".format(
    ms["title"],
    author["name"], author["surname"],
    now.year, now.month, now.day, now.hour, now.minute, 
    APP["name"], APP["version"]))

# -----------------------------------------------------------------------------
# write the common headers on all pages
# -----------------------------------------------------------------------------
def write_headers( f, author, manuscript ):
    write_blank_paragraph(f)
    f.write("{{\\header \\pard \\qr \\fs{0} {1} / {2} / \\chpgn \\par}}\n".format(FONT["size"], 
                    author["surname"], 
                    manuscript["runningtitle"].upper()))

# -----------------------------------------------------------------------------
# write the word count
# -----------------------------------------------------------------------------
def write_wordcount( f, numwords ):
    f.write("""
\\pard \\f{0} \\fs{1} \\qr
TMPPROX
\\par
\n""".format(FONT["tableid"], FONT["size"], str(numwords)))

# -----------------------------------------------------------------------------
# write the author information
# -----------------------------------------------------------------------------
def write_author( f, author ):
    f.write("""
\\pard \\f{0} \\fs{1} \\ql
{2} \\
{3} \\
{4}, {5} {6} \\
{7} \\
{8}
\\par
\n""".format(FONT["tableid"], FONT["size"], author["name"],
author["streetAddress"], author["addressLocality"], author["addressRegion"],
author["postalCode"], author["email"], author["phone"]))

# -----------------------------------------------------------------------------
# write the title
# -----------------------------------------------------------------------------
def write_title(f, manuscript, author):
    f.write("""
\\pard \\f{0} \\fs{1} \\sl{2} \\slmulti1 \\sb{3} \\qc {4} \\par
\\pard \\f{5} \\fs{6} \\sl{7} \\slmulti1 \\qc by \\
{8}\\
\par\n""".format(FONT["tableid"], FONT["size"], SPACING["paragraph"],
SPACING["titleskip"], manuscript["title"], FONT["tableid"], FONT["size"], SPACING["paragraph"], author["name"]))

# -----------------------------------------------------------------------------
# include the synopsis
# -----------------------------------------------------------------------------
def write_synopsis(f, synop):
    f.write("""
\\pard \\pagebb \\f{0} \\fs{1} \\sl{2} \\slmulti1 \\qc \\sb{3} \\sa{4} {{\\b
Synopsis }}
\par\n""".format(FONT["tableid"], FONT["size"], SPACING["paragraph"], SPACING["synopsisb"], SPACING["synopsisa"] )) 
    write_scene(f, synop)

# -----------------------------------------------------------------------------
# include the quote
# -----------------------------------------------------------------------------
def write_quote(f, quote):
    f.write("""
\\pard \\pagebb \\f{0} \\fs{1} \\sl{2} \\slmulti1 \\qc \\sb{3} \\sa{4}
\par\n""".format(FONT["tableid"], FONT["size"], SPACING["paragraph"], SPACING["quoteb"], SPACING["quotea"] ))
    write_scene(f, quote)

# -----------------------------------------------------------------------------
# finish things up and make a valid document
# -----------------------------------------------------------------------------
def write_postamble(f):
    f.write("\n}\n")

# -----------------------------------------------------------------------------
# write page break 
# -----------------------------------------------------------------------------
def write_pagebreak(f):
    f.write("\\pard \\pagebb \\par\n")

# -----------------------------------------------------------------------------
# write blank paragraph for spacing 
# -----------------------------------------------------------------------------
def write_blank_paragraph(f):
    f.write("\\pard {} \\par\n")

# -----------------------------------------------------------------------------
# write chapter headings
# -----------------------------------------------------------------------------
def write_chapter_heading(f, chapter, chapnum):
    chapnum = "CHAPTER {0}".format(chapnum)
    write_pagebreak(f)
    for x in range(16): 
        write_blank_paragraph(f)

    f.write("""
\\pard \\f{0} \\fs{1} \\sl{2} \\slmulti1 \\qc \\sa{3} {{\\tc\\b {4} }} \\par
\\pard \\f{5} \\fs{6} \\sl{7} \\slmulti1 \\qc \\sa{8} {{\\b {9} }}
\par\n""".format(
                FONT["tableid"], 
                FONT["size"], 
                SPACING["paragraph"],
                SPACING["newchapa"], 
                chapnum.upper(), 
                FONT["tableid"], 
                FONT["size"], 
                SPACING["paragraph"], 
                SPACING["chapsuba"], 
                chapter["title"]))

# -----------------------------------------------------------------------------
# write a single chapter
# -----------------------------------------------------------------------------
def write_chapter(f, chapter, chapnum):
    write_chapter_heading(f, chapter, chapnum)
    first = True
    for scene in chapter["scenes"]:
        if not first:
            write_scene_separator(f, scene)
        else:
            if core.settings["filescenesep"]:
                write_scene_separator(f, scene)
            first = False

        if not scene.endswith(".pdf"):
            write_scene(f, scene)
        # else:
            # It's an image
            # write_scan(f, scene)

# -----------------------------------------------------------------------------
# write a single scan 
# -----------------------------------------------------------------------------
def write_scan(f, scene):
    scenefile = core.get_scenefile( scene )

    if os.path.isfile(scenefile):
        f.write("{\\field \n{\*\\fldinst { INCLUDEPICTURE ")
        f.write("\"{}\"\n".format(scenefile))
        f.write("    \\\\* MERGEFORMAT \\\\d }}}\n")

# -----------------------------------------------------------------------------
# write a single scene 
# -----------------------------------------------------------------------------
def write_scene(f, scene):
    global CURSTATE
    scenefile = core.get_scenefile( scene )

    if os.path.isfile(scenefile):
        with open( scenefile, "r") as sfile:
            data = sfile.read()
            data = handle_footnotes(data)
            data = handle_comments(data)
            data = handle_links(data)
            # count the number of words in the file
            count = data.split()
            CURSTATE["numwords"] += len(count)
            data = sub_bold(data)
            data = sub_italics(data)
            data = data.strip()
            split = data.split("\n\n")
            for paragraph in split:
                paragraph = paragraph.strip()
                paragraph = re.sub(r'\s+', r' ', paragraph)
                if paragraph: 

                    if core.is_header(paragraph):
                        update_state("header")
                        paragraph = re.sub( '\n', ' ', paragraph)
                        paragraph = re.sub(r'^\s*\#+\s*', r'', paragraph)
                        f.write("\\pard \\fi0 \\sl{0} \\slmult1 \\f{1} \\fs{2} {{\\b {3}\\b0}}".
                            format(SPACING["paragraph"], FONT["tableid"], FONT["size"], paragraph))
                        f.write("\\par\n")

                    elif core.is_horrule(paragraph):
                        update_state("horrule")
                        f.write("\\pard \\qc \\fi0 \\sl{1} \\slmult1 \\f{2} \\fs{3} ".
                            format(SPACING["parindent"], SPACING["paragraph"], FONT["tableid"], FONT["size"]))
                        f.write( "###" )
                        f.write("\\par\n")

                    elif core.is_bulletlist_item(paragraph):
                        update_state("bulletlist")
                        paragraph = re.sub( '\n', ' ', paragraph)
                        paragraph = re.sub(r'^\s*\-\s*', r'', paragraph)
                        f.write("\\pard \\fi-{0} \\sl{1} \\slmult1 \\f{2} \\fs{3} \\li{4} \\bullet \\tab ".
                            format(SPACING["parindent"], SPACING["paragraph"], 
                                   FONT["tableid"], FONT["size"], SPACING["parindent"]))
                        f.write( paragraph )
                        f.write("\\par\n")

                    elif core.is_numberedlist_item(paragraph):
                        update_state("numberedlist")
                        paragraph = re.sub( '\n', ' ', paragraph)
                        paragraph = re.sub(r'^\s*[0-9]+\.', r'', paragraph)
                        f.write("\\pard \\fi-{0} \\sl{1} \\slmult1 \\f{2} \\fs{3} \\li{4} {5}. \\tab ".
                            format(SPACING["parindent"], SPACING["paragraph"], 
                                   FONT["tableid"], FONT["size"], SPACING["parindent"], CURSTATE["listnum"]))
                        f.write( paragraph )
                        f.write("\\par\n")

                    elif not paragraph.isspace():
                        update_state("paragraph")
                        paragraph = re.sub( '\n', ' ', paragraph)
                        f.write("\\pard \\fi{0} \\sl{1} \\slmult1 \\f{2} \\fs{3} ".
                            format(SPACING["parindent"], SPACING["paragraph"], FONT["tableid"], FONT["size"]))
                        f.write( paragraph )
                        f.write("\\par\n")
        return count
    else:
        print("ERROR: can't find scene file: " + scenefile)
        return 0

# -----------------------------------------------------------------------------
# write a scene separator
# -----------------------------------------------------------------------------
#TODO: add SPACING, etc. in this 
def write_scene_separator(f, scene):
    if core.settings["filescenesep"]:
        f.write("""\n\\pard \\sl480 \\slmulti1 \\qc \\sa720 ({0})
        \\par\n""".format(scene))
    else:
        f.write("\n\\pard \\sl480 \\slmulti1 \\qc \\sa720 ### \\par\n")

# -----------------------------------------------------------------------------
# iterate and write all the chapters
# -----------------------------------------------------------------------------
def write_chapters(f, manuscript):
    chapnum = 1
    for chapter in manuscript["chapters"]:
        if core.check_chapter_tags(chapter, core.settings["tags"]):
            write_chapter(f, chapter, chapnum)
            chapnum += 1

# -----------------------------------------------------------------------------
# handle footnotes 
# -----------------------------------------------------------------------------
def handle_footnotes( data ):
    if core.settings["footnotes"]: 
        # we are creating notes of some kind
            # inline footnotes
        inline = re.findall('\[\^(.+?)\][^\:]', data, re.MULTILINE)
        paired = re.findall('\[\^(.+?)\]\:(.+)', data, re.MULTILINE)
        d_paired = dict(paired)

        for note in inline:
            #  first, see if we have a paired footnote, and handle that
            if note in d_paired:
                # we sub the paired (bottom) part inline
                data = re.sub('\[\^{0}?\][^\:]'.format(note),
                    r"""{{\\super\\chftn}}{{\\footnote\\pard\\plain\\f{0}\\fs{1}\\chftn {2}}}""".format(FONT["tableid"], 
                    FONT["size"], d_paired[note]), data)
                # remove this element from the dictionary
                d_paired.pop(note)

            else:
                # if not, it's an inline note
                data = re.sub('\[\^{0}?\]'.format(note),
                    r"""{{\\super\\chftn}}{{\\footnote\\pard\\plain\\f{0}\\fs{1}\\chftn {2}}}""".format(FONT["tableid"], 
                    FONT["size"], note), data)

        # get rid of all bottom pairs, as these are not subbed above
        data  = re.sub('\[\^(.+?)\]\:(.+)', '', data)

    else:
        # we are removing footnotes
            # matches at the bottom of the page
        data  = re.sub('\[\^(.+?)\]\:(.+)', '', data)
            # inline 
        data  = re.sub('\[\^.+?\]', '', data)

    return data

# -----------------------------------------------------------------------------
# remove comments 
#
# TODO: handle the case in which a comment removes part of a footnote (there
# is no longer a match between the indicator of the note, and the footnote)
# -----------------------------------------------------------------------------
def handle_comments( data ):
    # we are removing them 
    data  = re.sub('\[comment]\:(.+)\n*', '', data)
    # data  = re.sub('\[comment]\:', '', data)

    return data

# -----------------------------------------------------------------------------
# handle hyperlinks 
# -----------------------------------------------------------------------------
def handle_links( data ):
    # inline
    data = re.sub('\[([^\]]*?)\]\(([^)]*?)\)', r'{\\field{\\fldinst HYPERLINK "\2"}{\\fldrslt \\ul \1}} ', data, flags=re.DOTALL)

    # find double bracketed 
    re_twobrackets = '\[([^\]]*?)\]\[([^\]]*?)\]'
    re_linkvalue   = '\[([^^][^\]]*?)\]\:([^\[]*)'
    inline = re.findall(re_twobrackets, data, flags=re.DOTALL)
    paired = re.findall(re_linkvalue, data, flags=re.DOTALL)
    d_paired = dict(paired)
    for link in inline:
        if link[1] in d_paired:
            sub = '\[{0}\]\[[^)]*?\]'.format(link[0])
            new = '{{\\\\field{{\\\\fldinst HYPERLINK "{0}"}}{{\\\\fldrslt \\\\ul {1}}}}} '.format(d_paired[link[1]], link[0]) 
            data = re.sub(sub, new,  data, flags=re.DOTALL)

    # find single bracketed 
    # re_brackets  = '[^\]]\s*?\[([^\]]*?)\]\s*?[^\[]'
    re_brackets  = '\[([^\]]*?)\][^:]'
    inline = re.findall(re_brackets, data, flags=re.DOTALL)
    for link in inline:
        if link in d_paired:
            sub = '\[{0}\][^:]'.format(link)
            new = '{{\\\\field{{\\\\fldinst HYPERLINK "{0}"}}{{\\\\fldrslt \\\\ul {1}}}}} '.format(d_paired[link], link) 
            data = re.sub(sub, new,  data, flags=re.DOTALL)

    # now remove all the links
    data = re.sub(re_linkvalue, "", data, flags=re.DOTALL)

    return data

# -----------------------------------------------------------------------------
# under certain conditions, substitute underlines for bold 
# -----------------------------------------------------------------------------
def sub_bold( data ):
    if core.settings["underline"]:
        data  = re.sub(r'\*\*([^*]+)\*\*', r'{\\ul \1\\ul0}', data)
    else:
        data  = re.sub(r'\*\*([^*]+)\*\*', r'{\\b \1\\b0}', data)
    return data

# -----------------------------------------------------------------------------
# under certain conditions, substitute underlines for italics 
# -----------------------------------------------------------------------------
def sub_italics( data ):
    if core.settings["underline"]:
        data  = re.sub(r'\*([^*]+)\*', r'{\\ul \1\\ul0}', data)
    else:
        data  = re.sub(r'\*([^*]+)\*', r'{\\i \1\\i0}', data)

    return data

# -----------------------------------------------------------------------------
# update the current state, based on modes 
# -----------------------------------------------------------------------------
def update_state( mode ):
    global CURSTATE
    if (mode == "numberedlist"):
        CURSTATE["listnum"] = CURSTATE["listnum"] + 1 
    else:
        CURSTATE["listnum"] = 0 

# -----------------------------------------------------------------------------
# update and translate rtf settings from the oms settings 
# -----------------------------------------------------------------------------
def update_state_from_settings():
    FONT["family"] = core.settings["font"]
    FONT["size"]   = 2*int(core.settings["fontsize"])
    if (FONT["family"] == "Courier"):
        FONT["tableid"] = "0"
    else:
        FONT["tableid"] = "1"

# -----------------------------------------------------------------------------
#
# execute
#
# -----------------------------------------------------------------------------
def write_rtf( ofile ):
    update_state_from_settings()

    with open( ofile, "w" ) as f:
        success = True

        write_preamble(f)
        write_docinfo(f, core.author, core.manuscript) 
        write_headers(f, core.author, core.manuscript) 
        write_wordcount(f, CURSTATE["numwords"])
        write_author(f, core.author)
        write_title(f, core.manuscript, core.author)

        if core.settings["synopsis"]:
            write_synopsis(f, core.get_synopsisfile())
        if core.settings["quote"]:
            write_quote(f, core.get_quotefile() )
        write_chapters(f, core.manuscript) 
        write_postamble(f)

        if (success != True):
            # remove the rtf file, it is incomplete
            print("ERROR: not writing rtf file")
        else:
            print("wrote file: " + core.settings["outputfile"])
        
    # substitute the total number of words
    newText = ""
    rounded = CURSTATE["numwords"] - CURSTATE["numwords"] % -100
    with open(core.settings["outputfile"], "r") as f:
        newText = f.read().replace("TMPPROX", 
                                   "approx. {} words".format(rounded))

    with open(core.settings["outputfile"], "w") as f:
        f.write(newText)


