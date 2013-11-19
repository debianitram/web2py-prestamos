#-*- encoding:utf-8 -*-
#
# Site: http://colmenalabs.com.ar
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
#    * ReporteBase.

from reportlab.lib import colors
from reportlab.lib.pagesizes import LEGAL, cm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.graphics.barcode import code39
from reportlab.platypus import Paragraph as Pg
from .common import config_font, stylePg
from gluon import current
from decimal import Decimal


class ReporteBase:

    _configPage = {'pagesize': LEGAL,
                   'leftMargin': 2 * cm,
                   'rightMargin': 1.5 * cm,
                   'topMargin': 2 * cm,
                   'bottomMargin': 1 * cm,
                   'showBoundary': 0}

    def __init__(self, filename, **conf):
        self.pagesize = LEGAL
        self.font = config_font()  # Ubuntu
        self.tableStyle = self.getTableStyle()
        self.filename = filename
        self.conf = conf or ReporteBase._configPage
        self.doc = self.settingDocument(self.filename, **self.conf)
        self.ver = "2.0"

    def settingDocument(self, filename, **config):
        return SimpleDocTemplate(filename, **config)

    def infoPage(self, canvas, doc):
        pass

    def getTableStyle(self):
        pass

    def render(self):
        pass