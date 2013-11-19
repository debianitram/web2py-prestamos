#-*- encoding:utf-8 -*-
#
# http://colmenalabs.com.ar
#
#            Colmena Labs (c) 2013.
#
# Programmer: Miranda Leiva, Martín Alejandro.
# E-mail: debianitram (at) gmail.com
#
# License Code:
# License Content:

# NOTA:
# This file contains:
#    *

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from gluon import current
import os


font = 'Ubuntu'
w2p_folder = current.request.folder


def config_font():
    path_font = os.path.join(w2p_folder, 'static/font_ubuntu/')
    pdfmetrics.registerFont(TTFont('Ubuntu',
                                    path_font + 'Ubuntu-R.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuB',
                                    path_font + 'Ubuntu-B.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuBI',
                                    path_font + 'Ubuntu-BI.ttf'))
    pdfmetrics.registerFont(TTFont('UbuntuRI',
                                    path_font + 'Ubuntu-RI.ttf'))
    pdfmetrics.registerFontFamily('Ubuntu', normal='Ubuntu',
                                             bold='UbuntuB',
                                             italic='UbuntuRI',
                                             boldItalic='UbuntuBI')

    return {'normal': 'Ubuntu',
            'bold': 'UbuntuB',
            'italic': 'UbuntuRI',
            'boldItalic': 'UbuntuBI'}


def stylePg(fontsize=10, alignment='left'):
    enums = {'left': 0,
             'center': 1,
             'right': 2,
             'justify': 4}

    return ParagraphStyle('',
                    fontName=font,
                    fontSize=fontsize,
                    alignment=enums[alignment],
                    spaceAfter=0)
