#!/usr/bin/env python
# coding: utf8
# Colmena Labs - Soluciones Tecnológicas
# debianitram (at) gmail.com

from gluon.dal import Field
from gluon.validators import IS_NOT_EMPTY, IS_NOT_IN_DB, IS_IN_SET, IS_IN_DB
from gluon.html import TABLE, THEAD, TBODY, TR, TH, TD, SPAN, I, URL, H4, H5
from gluon.html import STRONG, TAG, HR, CENTER, STYLE, INPUT, TAG, SCRIPT, A
from objeto_base import objbase
from decimal import Decimal

class prestamo(objbase):

    def __init__(self, container):
        super(prestamo, self).__init__(container)
        self.tipo_credito = {1: 'diario', 7: 'semanal', 30: 'mensual'}
        self.estado = {1: 'vigente', 2: 'finalizado', 3: 'cancelado'}
        
    def define_tables(self):
        db = self.container.db
        auth = self.container.auth
        
        db.define_table(self.name_table,
            Field('cliente_id', db.cliente),
            Field('fecha', 'date'),
            Field('monto', 'decimal(6, 2)'),
            Field('concepto', 
                  'reference %s' % self.container.concepto_prestamo.name_table),
            Field('tipo_credito', 'list:string'),
            Field('cuotas', 'integer'),
            Field('interes', 'integer'),
            Field('monto_total', 'decimal(6, 2)',
                  compute=lambda r: self.monto_total(r['monto'], r['interes'])),
            Field('observacion', 'text'),
            Field('estado', 'list:string', default=1),
            auth.signature,
            format='%(id)s:%(cliente_id)s->%(fecha)s',
            common_filter=lambda q: db[self.name_table].is_active == True
            )

        # Configuraciones
        self.labels(db[self.name_table])
        self.readables_writables(db[self.name_table])
        self.requires(db[self.name_table])
        self.represent(db[self.name_table])

    # Configuraciones.
    def labels(self, dbconf):
        dbconf.id.label = 'ID'
        dbconf.cliente_id.label = 'Cliente'
        dbconf.fecha.label = 'Fecha emisión'
        dbconf.monto.label = 'Importe ($)'
        dbconf.tipo_credito.label = 'Tipo de Crédito'
        dbconf.interes.label = '% interés'
        dbconf.monto_total.label = 'Importe Financiado ($)'
        dbconf.observacion.label = 'Observaciones'

    def readables_writables(self, dbconf):
        dbconf.id.readable = dbconf.id.writable = False
        # dbconf.cont_cuotas.readable = dbconf.cont_cuotas.writable = False
        dbconf.estado.readable = dbconf.estado.writable = False

    def requires(self, dbconf):
        concepto = self.container.concepto_prestamo
        dbconf.fecha.requires = dbconf.monto.requires = IS_NOT_EMPTY()
        dbconf.cuotas.requires = IS_NOT_EMPTY()
        dbconf.interes.requires = IS_NOT_EMPTY()
        dbconf.tipo_credito.requires = IS_IN_SET(self.tipo_credito)
        setconcepto = concepto.search('id', 'greater', get_set=True)
        dbconf.concepto.requires = IS_IN_DB(setconcepto,
                                            dbconf._db[concepto.name_table].id,
                                            '%(nombre)s')
        dbconf.estado.requires = IS_IN_SET(self.estado)

    def represent(self, dbconf):
        dbconf.tipo_credito.represent = lambda v: self.tipo_credito[int(v[0])]
        dbconf.estado.represent = lambda v: self.estado[int(v[0])]

    # Controles.
    def monto_total(self, monto, interes):
        # Monto sumado el porcentaje de interes.
        return Decimal(monto) + (int(interes) * Decimal(monto) / 100)

    def valor_cuota(self, monto_total, cuota):
        return Decimal(monto_total) / int(cuota)

    def deudas(self, cliente_id):
        dbprestamo = self.container.db[self.name_table]
        query = dbprestamo.cliente_id == cliente_id
        query &= dbprestamo.estado == 1

        f = self.getFields('id', 'fecha', 'concepto', 'monto', \
                           'cuotas', 'interes', 'monto_total')
        return self.container.db(query).select(*f, 
                                                orderby=~dbprestamo.created_on)

    def resumen_deudas(self, cliente_id):
        # Datos para el comportamiento AJAX
        cmd = "ajax('%s', ['%s'], '%s');"
        cmd_cancel = "ajax('%s', ['%s'], ':eval');"
        target = 'detalle_prestamo'
        cancel = 'cancelar_prestamo'
        ######################################

        fields = self.getFields('id', 'fecha', 'concepto', 'monto', \
                                'cuotas', 'interes', 'monto_total')
        
        thead = THEAD(TR(*[TH(f.label) for f in fields]))
        table = TABLE(thead, _class='table table-striped table-bordered')
        tbody = TBODY()

        rows = self.deudas(cliente_id)

        if not rows:
            return H4('No presenta deudas', _class='alert alert-success')

        for row in self.deudas(cliente_id):
            tbody.append(TR(TD(row.id),
                            TD(row.fecha),
                            TD(row.concepto.nombre),
                            TD(row.monto),
                            TD(row.cuotas),
                            TD(row.interes),
                            TD(row.monto_total),
                            TD(CENTER(
                                SPAN(I(_class='icon-zoom-in'), ' detalle',
                                    _id=row.id,
                                    _title='Ver detalle del prestamos',
                                    _class='btn btn-mini',
                                    _onclick=cmd % (URL(target,
                                                        vars=dict(pid=row.id),
                                                        user_signature=True),
                                                    None,
                                                    target)
                                    ))),
                            TD(CENTER(
                                SPAN(I(_class='icon-remove'), ' cancelar',
                                    _id='cancel %s' % row.id,
                                    _title='Cancelar el prestamo',
                                    _class='btn btn-mini',
                                    _onclick='cancelar(%s);' % row.id)
                                )),
                            _id='dresumen_tr_%s' % row.id)
                        )

        table.append(tbody)

        # INPUT que contendrá el IDCuota que será enviado a través de ajax.
        idprestamo = INPUT(_type='hidden', _id='IDPrestamo', _name='idprestamo')
        url = URL('prestadmin', 'cancelar_prestamo', user_signature=True)
        
        javascript = """
            function cancelar(prestamo){
                jQuery('#IDPrestamo').val(prestamo);
                if(confirm('Desea cancelar el Prestamo?')){
                    ajax('%s', ['idprestamo'], ':eval');
                }
                else {
                    jQuery('#IDPrestamo').val('');
                }
            }
        """ % url

        return TAG[''](table, idprestamo, SCRIPT(javascript))

    def detalle(self, prestamo_id):
        cuota = self.container.cuota
        separador = HR(_class='bs-docs-separator')
        title = H4('Detalle del prestamo')

        prestamo = self.search('id', 'equal', prestamo_id).first()

        body = [TR(TD(title, _colspan=3),
                    TD(A(I(_class='icon-print'), ' Planilla control',
                        _href=URL('prestadmin', 'planilla_prestamo',
                                  args=(prestamo.id),
                                  user_signature=True),
                        _class='btn btn-mini'),
                    _style='vertical-align:middle;')
                ),
                TR(
                    TD(STRONG('Crédito ID:'), _width="10%"),
                    TD(prestamo.id, _width="30%"),
                    TD(STRONG('F. Emisión:'), _style='text-align:right'),
                    TD(prestamo.fecha)
                ),
                TR(
                    TD(STRONG('Concepto:')),
                    TD(prestamo.concepto.nombre),
                    TD(STRONG('Importe:'), _style='text-align:right'),
                    TD('$ ', prestamo.monto)
                ),
                TR(
                    TD(STRONG('Intereses:')),
                    TD('% ', prestamo.interes),
                    TD(STRONG('Cuotas:'), _style='text-align:right'),
                    TD(prestamo.cuotas)
                ),
                TR(
                    TD(STRONG('Importe Financiado:'), 
                        _colspan=3, 
                        _style='text-align:right'),
                    TD(STRONG('$ ', prestamo.monto_total, 
                              _style='color:#DB2525'), _width="20%")
                ),
                TR(
                    TD(STRONG('Observaciones:')),
                    TD(prestamo.observacion, _colspan=2)
                )]
        table = TABLE(TBODY(*body),
                      _valign="middle",
                      _class='table table-condensed', 
                      _style='width:80%')

        tag_detalle = TAG[''](separador, 
                              table,
                              cuota.resumen(prestamo.id))

        return tag_detalle



class concepto_prestamo(objbase):

    def __init__(self, container):
        super(concepto_prestamo, self).__init__(container)
                
    def define_tables(self):
        db = self.container.db
        auth = self.container.auth
        
        db.define_table(self.name_table,
            Field('nombre', unique=True),
            Field('descripcion'),
            auth.signature,
            format='%(nombre)s'
            )

        # Configuraciones
        # self.requires(db[self.name_table])

