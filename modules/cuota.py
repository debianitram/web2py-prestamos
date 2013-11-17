#!/usr/bin/env python
# coding: utf8
# Colmena Labs - Soluciones Tecnológicas
# debianitram (at) gmail.com

from gluon.dal import Field
from gluon.validators import IS_NOT_EMPTY, IS_NOT_IN_DB, IS_IN_SET
from gluon.html import TABLE, THEAD, TBODY, TR, TH, TD
from gluon.html import SCRIPT, CENTER, URL, INPUT, H4, SPAN, I, HR, TAG
from gluon.http import redirect
from objeto_base import objbase
from datetime import date, timedelta
from decimal import Decimal

class cuota(objbase):

    def __init__(self, container):
        super(cuota, self).__init__(container)
        self.estado = {1: 'pendiente', 2: 'pagada', 3: 'mora', 4: 'cancelada'}
        
    def define_tables(self):
        db = self.container.db
        auth = self.container.auth
        
        db.define_table(self.name_table,
            Field('prestamo_id', db.prestamo),
            Field('nro', 'integer'),
            Field('valor_cuota', 'decimal(6, 2)'),
            Field('fecha_limite', 'date'),
            Field('fecha_pago', 'date'),
            Field('estado', 'list:string', default=1),
            Field('cod_year_month', 'string',
                  compute=lambda r: r['fecha_limite'].strftime('%Y-%m')),
            auth.signature,
            format='%(prestamo_id)s')

        # Configuración
        self.labels(db[self.name_table])
        self.requires(db[self.name_table])
        self.represent(db[self.name_table])

    # Configuración
    def labels(self, dbconf):
        dbconf.nro.label = 'Nº Cuota'
        dbconf.fecha_limite.label = 'Fecha Límite'

    def readables_writables(self, dbconf):
        dbconf.prestamo_id.writable = False
        dbconf.fecha_pago.readable = dbconf.fecha_pago.writable = False
        dbconf.estado.writable = False

    def requires(self, dbconf):
        dbconf.estado.requires = IS_IN_SET(self.estado)

    def represent(self, dbconf):
        dbconf.estado.represent = lambda v, r: self.get_estado(r)

    # Controles
    def get_estado(self, row_cuota):
        """
        #  Colores de estados:
        #  Amarillo: Pendiente -> 1
        #  Verde: Pagado -> 2
        #  Rojo: Mora -> 3.
        """

        if row_cuota.estado[0] == '2':
            return SPAN(self.estado[2], 
                        _class='label label-success')
        elif row_cuota.estado[0] == '4':
            return SPAN(self.estado[4],
                        _class='label')
        else:
            if row_cuota.fecha_limite >= date.today():
                return SPAN(self.estado[1],
                            _class='label label-warning')
            elif row_cuota.fecha_limite < date.today():
                dias_mora = date.today() - row_cuota.fecha_limite
                return SPAN(self.estado[3], 
                            _class='label label-important',
                            _title='Días de mora: %s' % dias_mora)

    def resumen(self, prestamo_id):
        #### Resumen de cuotas por prestamo.
        """ El método presenta un resumen detallado de las cuotas
            que pertenecen a ciertos prestamos/créditos de un cliente.
            Forma de presentación:

            |Nº Cuota| Importe| Fecha Límite| Estado| Fecha de Pago| Btn Abonar

            NOTA:
            Btn Abonar llama una acción para poder registar el pago de una cuota

        """
        sepadador = HR(_class='bs-docs-separator')

        # INPUT que contendrá el IDCuota que será enviado a través de ajax.
        input_ = INPUT(_type='hidden', _id='IDCuota', _name='idcuota')

        cuotas = self.search('prestamo_id', 
                             'equal', 
                             prestamo_id,
                             orderby=self.container.db[self.name_table].id)
        

        fields = self.getFields('fecha_limite', 'estado', 'fecha_pago')
        tr_head = TR(TH('Nº Couta'), TH('Importe'))
        [tr_head.append(TH(f.label)) for f in fields]
        table = TABLE(THEAD(tr_head), 
                      _class='table table-striped table-condensed')

        tbody = TBODY()
        for cuota in cuotas:
            tbody.append(TR(
                    TD(cuota.nro),
                    TD("$%.2f" % cuota.valor_cuota),
                    TD(cuota.fecha_limite),
                    TD(self.get_estado(cuota)),
                    TD(cuota.fecha_pago or '-'),
                    TD(CENTER(SPAN(I(_class='icon-download-alt'), 
                                    ' Abonar', 
                                    _onclick='func_abonar(%s)' % cuota.id,
                                    _class='btn btn-mini'))
                       ) if cuota.estado[0] != '2' else '',
                            _id='tr_cuota_%s' % cuota.id
                            )
                        )
        table.append(tbody)

        url = URL('cuotas', 'abonar_cuota', user_signature=True)
        javascript = """
            function func_abonar(cuotaid){
                jQuery('#IDCuota').val(cuotaid);
                if(confirm('Desea aceptar el pago?')){
                    ajax("%s", ['idcuota'], 'tr_cuota_' + cuotaid);
                }
                else {
                    alert('Canceló el pago!')
                }
            }
        """ % url
        
        return TAG[''](sepadador, input_, table, SCRIPT(javascript))

    def generar(self, form, insert=False):
        prestamo = self.container.prestamo

        if form.vars.fecha == "" or form.vars.tipo_credito == "" \
            or form.vars.monto == "" or form.vars.cuotas == "" or \
            form.vars.interes == "":
            return SPAN("Complete los campos que se encuentran marcados con (*)",
                   _class='label label-important')

        else:
            FECHA = date(*[int(i) for i in form.vars.fecha.split('-')])
            TIPO_CREDITO = int(form.vars.tipo_credito)
            MONTO = Decimal(form.vars.monto)
            CUOTAS = int(form.vars.cuotas)
            INTERES = int(form.vars.interes)
            TOTAL = prestamo.monto_total(MONTO, INTERES)
            VALOR_CUOTA = prestamo.valor_cuota(TOTAL, CUOTAS)

            #  Insertamos los valores a la base de datos.
            if insert:
                dbcuota = self.container.db[self.name_table]
                for c in range(1, CUOTAS + 1):
                    dbcuota.insert(
                            nro=c,
                            prestamo_id=form.vars.id,
                            valor_cuota=VALOR_CUOTA,
                            fecha_limite=FECHA + timedelta(c * TIPO_CREDITO)
                            )

                dbcuota._db.commit()
                return

            else:
                encabezado = ('Nº Cuota', 'Importe', 'Fecha Pago')
                thead = THEAD(TR(*[TH(i) for i in encabezado]))
                table = TABLE(thead, _class='table table-condensed')
                tbody = TBODY()

                for c in range(1, CUOTAS + 1):
                    tbody.append(TR(
                                    TD(c),
                                    TD("$%.2f" % VALOR_CUOTA),
                                    TD(FECHA + timedelta(c * TIPO_CREDITO))
                                    )
                                )
                tbody.append(TR(TD('TOTAL:'),
                                TD("$%.2f" % TOTAL,
                                    _style="color:red",
                                    _colspan=2)))
                table.append(tbody)
                return table

    def abonar(self, request):
        cuota_id = request.vars.get('idcuota')
        prestamo = self.container.prestamo
        db = self.container.db
        tbcuota = db[self.name_table]
        tbprestamo = db[prestamo.name_table]


        c = tbcuota(cuota_id)
        c.update_record(fecha_pago=date.today(), estado=2)
        
        q = db((tbcuota.prestamo_id == c.prestamo_id) & (tbcuota.estado != 2))

        if q.count() == 0:
            #  Si los estados de cuotas del prestamos son distintas de 2
            #  cambiamos el estado del prestamo a finalizado.
            tbprestamo(c.prestamo_id).update_record(estado=2)
            db.commit()
            message = 'Finalizó el crédito: %s exitosamente' % c.prestamo_id
            self.container.env.session.flash = message
            redirect(URL('clientes', 'index', 
                        args=['view', 'cliente', c.prestamo_id.cliente_id],
                        user_signature=True,
                        extension=False), client_side=True)
        else:
            tags = TAG[''](TD(c.nro), 
                           TD("$%.2f" % c.valor_cuota),
                           TD(c.fecha_limite),
                           TD(SPAN('pagada', _class='label label-success')),
                           TD(c.fecha_pago),
                           TD(''))

        db.commit()
        return tags

    def calculo_periodo(self, periodo):
        """ 
            periodo debe tener la forma 'yyyy-mm'. Ej: '2013-11'
            Calculamos:
            * Cantidad de Cuotas en un periodo.
            * Cantidad de Cuotas abonadas en ese periodo.
            * Total en Pesos ($) de las cuotas abonadas en ese periodo
         """
        db = self.container.db
        tbcuota = db[self.name_table]

        ### Cuotas en un periodo determinado.
        cuotas_periodo = tbcuota.cod_year_month == periodo
        cant_cuotas = db((cuotas_periodo) & (tbcuota.estado != 4)).count()
        cuotas_periodo &= tbcuota.estado == 2
        # Total en Pesos ($) de cuotas abonadas en un periodo determinado.
        cant_cuotas_abonadas = db(cuotas_periodo).count()
        total_abonadas = sum([c.valor_cuota \
                for c in db(cuotas_periodo).select(tbcuota.valor_cuota)])

        # Porcentaje de Cuota abonadas en un periodo sobre las cuotas
        # existentes en ese periodo.
        # cant_cuotas_abonadas * 100 / cant_cuotas
        try:
            x = round(cant_cuotas_abonadas * 100.0 / cant_cuotas)
            xcien = (x, 100 - x)
        except ZeroDivisionError:
            xcien = (0, 0)

        return (cant_cuotas, 
                cant_cuotas_abonadas, 
                total_abonadas,
                xcien)

    def reporte_diario(self, fecha):
        db = self.container.db
        tbcuota = db[self.name_table]
        if isinstance(fecha, date):
            fecha = fecha
        else:
            fecha = date(*[int(f) for f in fecha.split('-')])
        # Consultas.
        periodo_actual = fecha.strftime('%Y-%m')

        # Q_PERIODO = Cuotas por periodo
        # Q_ABONADAS = Cantidad de Cuotas Abonadas en ese Periodo
        # TQ_ABONADAS = Total en Pesos ($) de Cuotas Abonadas en ese Periodo
        Q_PERIODO, Q_ABONADAS, TQ_ABONADAS, G_XCIEN \
            = self.calculo_periodo(periodo_actual)
        # Porcentaje de Cuotas Abonadas.

        # Calculamos las cuotas abonadas de un día determinado (date)
        QAbonadas = tbcuota.fecha_pago == fecha
        rows_abonadas = db(QAbonadas).select(tbcuota.cod_year_month,
                                             tbcuota.valor_cuota,
                                             tbcuota.estado)
        # Cantidad de cuotas abonadas en un día determinado (date)
        Q_ABONADAS_DATE = db(QAbonadas).count() 
        # Total de cuotas abonadas - Calculo en Pesos de un día determinado
        TQ_ABONADAS_DATE = sum([c.valor_cuota for c in rows_abonadas])

        return dict(periodo=periodo_actual,
                    Q_PERIODO=Q_PERIODO,
                    Q_ABONADAS=Q_ABONADAS,
                    TQ_ABONADAS=TQ_ABONADAS,
                    Q_ABONADAS_DATE=Q_ABONADAS_DATE,
                    TQ_ABONADAS_DATE=TQ_ABONADAS_DATE,
                    G_XCIEN=G_XCIEN)

        