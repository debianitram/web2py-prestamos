#!/usr/bin/env python
# coding: utf8
# Colmena Labs - Soluciones Tecnológicas
# debianitram (at) gmail.com

from gluon.dal import Field
from gluon.validators import IS_NOT_EMPTY, IS_NOT_IN_DB, IS_IN_SET
from gluon.html import URL
from gluon.http import redirect
from objeto_base import objbase

class cliente(objbase):

    def __init__(self, container):
        super(cliente, self).__init__(container)
        self.tipo = ('titular', 'chofer')
        
    def define_tables(self):
        db = self.container.db
        auth = self.container.auth
        
        db.define_table(self.name_table,
            Field('nombre'),
            Field('apellido'),
            Field('dni', 'integer', unique=True),
            Field('domicilio'),
            Field('telefono'),
            Field('codsearch', 
                  compute=lambda r: r['nombre'] + r['apellido'] + str(r['dni'])),
            Field('tipo_cliente', 'list:string'),
            Field('movil'),
            auth.signature,
            migrate=True,
            format='%(apellido)s, %(nombre)s',
            common_filter=lambda q: db[self.name_table].is_active == True,
            )

        # Configuraciones
        self.labels(db[self.name_table])
        self.readables_writables(db[self.name_table])
        self.requires(db[self.name_table])

    # Configuraciones.
    def labels(self, dbconf):
        dbconf.dni.label = 'Nº Documento'
        dbconf.tipo_cliente.label = 'Cliente Tipo'
        dbconf.movil.label = 'Unidad Móvil'

    def readables_writables(self, dbconf):
        dbconf.id.readable = dbconf.id.writable = False
        dbconf.codsearch.readable = False

    def requires(self, dbconf):
        dbconf.nombre.requires = dbconf.apellido.requires = IS_NOT_EMPTY()
        _set = self.search('id', 'greater', get_set=True)
        dbconf.dni.requires = IS_NOT_IN_DB(_set, dbconf.dni)
        dbconf.tipo_cliente.requires = IS_IN_SET(self.tipo)

    def ui_grid(self):
        return dict(widget='table',
                    header='',
                    content='alert',
                    default='',
                    cornerall='',
                    cornertop='',
                    cornerbottom='',
                    button='button',
                    buttontext='buttontext button',
                    buttonadd='icon plus icon-plus',
                    buttonback='icon leftarrow icon-arrow-left',
                    buttonexport='icon downarrow icon-download',
                    buttondelete='icon trash icon-trash',
                    buttonedit='icon pen icon-pencil',
                    buttontable='icon rightarrow icon-arrow-right',
                    buttonview='icon magnifier icon-zoom-in',
                    )

    # Controles
    def oncreate(self, form):
        msg = 'Añadió un cliente éxitosamente'
        self.container.env.session.flash = msg
        redirect(URL(c='clientes', f='index',
                     args=['view', self.name_table, form.vars.id],
                     user_signature=True))

    def get_name(self, row):
        return "%(apellido)s, %(nombre)s" % row


