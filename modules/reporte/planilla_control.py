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
#    * planilla_control.

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Paragraph as Pg
from .common import config_font, stylePg
from gluon import current
from reporte.reporte_base import ReporteBase
from reporte.numtoword import numToWord
from decimal import Decimal


class planilla_control(ReporteBase):

    _configPage = {'pagesize': A4,
                   'leftMargin': 2 * cm,
                   'rightMargin': 2 * cm,
                   'topMargin': 2 * cm,
                   'bottomMargin': 2 * cm,
                   'showBoundary': 0}

    def __init__(self, filename, prestamo_id):
        ReporteBase.__init__(self,
                            filename,
                            **planilla_control._configPage)
        self.db = self.proccesing(prestamo_id)


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

    def proccesing(self, prestamo_id):
        db = current.globalenv.get('db')
        prestamo = current.globalenv.get('container').prestamo
        p = prestamo.search('id', 'equal', prestamo_id).first()
        return dict(prestamo=p, rows_cuotas=p.cuota.select())

    def getTableStyle(self):
        T_ENCABEZADO = TableStyle([
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('LINEABOVE',(0, 1), (-1, 1), 1, colors.black),
                        ('LINEABOVE',(0, 4), (-1, 4), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BACKGROUND', (0, 1), (0, 2), colors.lightgrey),
                        ('BACKGROUND', (0, 4), (0, 5), colors.lightgrey),
                        ('BACKGROUND', (2, 1), (2, 1), colors.lightgrey),
                        ('BACKGROUND', (2, 4), (2, 5), colors.lightgrey),
                        ('SPAN', (0, 0), (1, 0)),
                        ('SPAN', (0, 3), (-1, 3)),
                        ])

        T_RESUMEN = TableStyle([
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ])

        return dict(encabezado=T_ENCABEZADO, resumen=T_RESUMEN)

    def t_encabezado(self):
        #  Labels
        prestamo = self.db['prestamo']
        titulo = Pg("<b>%s</b>" % 'PLANILLA DE CONTROL DE PAGO',
                    stylePg(12))
        detalle = Pg("<b>%s</b>" % 'DETALLE DEL PRESTAMO',
                    stylePg(12))

        l_fecha = Pg('Fecha:', stylePg(alignment='right'))
        l_nombre = Pg('Nombre:', stylePg(alignment='right'))
        l_apellido = Pg('Apellido:', stylePg(alignment='right'))
        l_movil = Pg('Móvil:', stylePg(alignment='right'))
        l_concepto = Pg('Concepto:', stylePg(alignment='right'))
        l_importe = Pg('Importe Total:', stylePg(alignment='right'))
        l_prestamo_id = Pg('Prestamo ID:', stylePg(alignment='right'))
        l_nro_cuotas = Pg('Nº Cuotas:', stylePg(alignment='right'))

        r_fecha = Pg('%s' % prestamo.fecha, stylePg(11))
        r_nombre = Pg(prestamo.cliente_id.nombre, stylePg(11))
        r_apellido = Pg(prestamo.cliente_id.apellido, stylePg(11))
        r_movil = Pg(prestamo.cliente_id.movil, stylePg(11))
        r_concepto = Pg(prestamo.concepto.nombre, stylePg(11))
        r_importe = Pg('<b>$%.2f</b>' % prestamo.monto_total, stylePg(11))
        r_prestamo_id = Pg('<b>%s</b>' % str(prestamo.id).zfill(6),
                   stylePg(11))
        r_nro_cuotas = Pg('%s' % prestamo.cuotas, stylePg(11))

        encabezado = [
                [titulo, '', l_fecha, r_fecha],
                [l_nombre, r_nombre, l_movil, r_movil],
                [l_apellido, r_apellido, '', ''],
                [detalle, '', '', ''],
                [l_concepto, r_concepto, l_importe, r_importe],
                [l_prestamo_id, r_prestamo_id, l_nro_cuotas, r_nro_cuotas],
        ]

        return Table(encabezado, 
                     [2.78 * cm, 7.14 * cm, 3.33 * cm, 3.76 * cm],
                     style=self.tableStyle.get('encabezado'))

    def t_resumen(self):
        cuota = self.db['rows_cuotas']
        #  Labels
        l_nro = Pg("CUOTA", stylePg(alignment='center'))
        l_fecha = Pg("FECHA", stylePg(alignment='center'))
        l_pago = Pg("PAGO", stylePg(alignment='center'))
        l_firma = Pg('FIRMA', stylePg(alignment='center'))

        # Response
        resumen = [[l_nro, l_fecha, l_pago, l_firma]]

        for c in cuota:
            resumen.append([
                        Pg('%s' % c.nro, stylePg(alignment='center')),
                        Pg('%s' % c.fecha_limite, stylePg(alignment='center')),
                        '',
                        ''])

        return Table(resumen, 
                     [2.20 * cm, 5 * cm, 2.73 * cm, 7.09 * cm],
                     style=self.tableStyle.get('resumen'))

    def render(self):
        self.story = list()
        self.story.append(self.t_encabezado())
        self.story.append(Spacer(1 * cm, 1 * cm))
        self.story.append(self.t_resumen())
        self.doc.build(self.story, onFirstPage=self.infoPage)
