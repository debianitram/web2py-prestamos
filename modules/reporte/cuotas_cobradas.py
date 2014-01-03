#-*- encoding:utf-8 -*-
#
# Sistema de prestamos
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
#    * cuotas_cobradas.

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Paragraph as Pg
from .common import config_font, stylePg
from gluon import current
from reporte.reporte_base import ReporteBase
from reporte.numtoword import numToWord
from decimal import Decimal


class cuotas_cobradas(ReporteBase):

    _configPage = {'pagesize': A4,
                   'leftMargin': 2 * cm,
                   'rightMargin': 2 * cm,
                   'topMargin': 2 * cm,
                   'bottomMargin': 2 * cm,
                   'showBoundary': 0}

    def __init__(self, filename, **fechas):
        ReporteBase.__init__(self,
                            filename,
                            **cuotas_cobradas._configPage)
        self.db = self.proccesing(**fechas)


    def infoPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.font['normal'], 12)
        info = "Colmena Labs - Soluciones tecnológicas (*) "
        info += "www.colmenalabs.com.ar - Página: %s" % doc.page
        info_up = "Sistema de Prestamos - Villa Parque"
        canvas.setFontSize(10)
        canvas.drawRightString(18 * cm, 28 * cm, info_up)
        canvas.drawString(2 * cm, 1 * cm, "%s" % info)
        canvas.restoreState()

    def proccesing(self, **fechas):
        db = current.globalenv.get('db')
        cuota = current.globalenv.get('container').cuota
        dbcuota = db[cuota.name_table]

        fields = cuota.getFields('id', 
                                 'nro',
                                 'fecha_pago',
                                 'prestamo_id',
                                 'valor_cuota')

        q = dbcuota.fecha_pago >= fechas['desde']
        q &= dbcuota.fecha_pago <= fechas['hasta']
        results = db(q)

        return dict(cuotas=results.select(*fields, orderby=dbcuota.fecha_pago), 
                    fechas=fechas,
                    total_cobros=results.count())

    def getTableStyle(self):
        T_ENCABEZADO = TableStyle([
                        ('BOX', (0, 0), (-1, -1), .5, colors.black),
                        ('LINEABOVE',(0, 1), (-1, 1), .5, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BACKGROUND', (0, 1), (0, 2), colors.lightgrey),
                        ('BACKGROUND', (2, 1), (2, 1), colors.lightgrey),
                        ('SPAN', (0, 0), (1, 0)),
                        ])

        T_RESUMEN = TableStyle([
                        ('BOX', (0, 0), (-1, -1), .5, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), .5, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('SPAN', (0, -2), (3, -2)),
                        ('SPAN', (1, -1), (-1, -1))
                        ])

        return dict(encabezado=T_ENCABEZADO, resumen=T_RESUMEN)

    def t_encabezado(self):
        #  Labels
        titulo = Pg("<b>%s</b>" % 'LISTA DE CUOTAS COBRADAS ENTRE DOS FECHAS',
                    stylePg(11))

        l_fecha = Pg('Fecha:', stylePg(alignment='right'))
        l_desde = Pg('Desde:', stylePg(alignment='right'))
        l_hasta = Pg('Hasta:', stylePg(alignment='right'))
        l_total_cobros = Pg('Total cobros:', stylePg(alignment='right'))

        r_fecha = Pg('%s' % current.request.now.date(), stylePg(11))
        r_desde = Pg('%s' % self.db['fechas']['desde'], stylePg(11))
        r_hasta = Pg('%s' % self.db['fechas']['hasta'], stylePg(11))
        r_total_cobros = Pg('%s' % self.db['total_cobros'], stylePg(11))

        encabezado = [
                [titulo, '', l_fecha, r_fecha],
                [l_desde, r_desde, l_hasta, r_hasta],
                [l_total_cobros, r_total_cobros, '', '']
                ]

        return Table(encabezado, 
                     [2.78 * cm, 7.14 * cm, 3.33 * cm, 3.76 * cm],
                     style=self.tableStyle.get('encabezado'))

    def t_resumen(self):
        cuotas = self.db['cuotas']
        config = current.globalenv.get('config')
        #  Labels
        l_id = Pg("ID CUOTA", stylePg(alignment='center'))
        l_nro = Pg("NRO CUOTA", stylePg(alignment='center'))
        l_fecha = Pg("FECHA COBRO", stylePg(alignment='center'))
        l_cliente = Pg("CLIENTE", stylePg())
        l_importe = Pg('IMPORTE', stylePg())

        # Response
        resumen = [[l_id, l_nro, l_fecha, l_cliente, l_importe]]

        total = sum([c.valor_cuota for c in cuotas])
        total_str = str(total).split('.')
        total_letras = '%s con %s/100' % (numToWord(int(total_str[0])),
                                          total_str[1].ljust(2, '0'))

        for c in cuotas:
            resumen.append([
                        Pg('%s' % c.id, stylePg(alignment='center')),
                        Pg('%s' % c.nro, stylePg(alignment='center')),
                        Pg('%s' % c.fecha_pago, stylePg(alignment='center')),
                        Pg('%s' % config.client_name(c.prestamo_id.cliente_id),
                            stylePg()),
                        Pg('$%.2f' % c.valor_cuota, stylePg())
                        ])

        resumen.append([Pg('Saldo Total', stylePg(alignment='right')),
                        '', '', '', Pg('<b>$%.2f</b>' % total, stylePg(12))])
        resumen.append([Pg('Son pesos:', stylePg(alignment='right')),
                        Pg(total_letras, stylePg()), '', '', ''])

        return Table(resumen, 
                    [2.19 * cm, 2.53 * cm, 3.32 * cm, 5.55 * cm, 3.40 * cm],
                    style=self.tableStyle.get('resumen'))

    def render(self):
        self.story = list()
        self.story.append(self.t_encabezado())
        self.story.append(Spacer(1 * cm, 1 * cm))
        self.story.append(self.t_resumen())
        self.doc.build(self.story, onFirstPage=self.infoPage)
