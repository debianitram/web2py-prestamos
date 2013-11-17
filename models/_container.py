#-*- encoding:utf-8 -*-
#
# SAISE. Sistema Administrativo Integrador & Seguimiento de Expedientes.
# Módulo: {Nombre del módulo}
# Site: www.colmenalabs.com.ar
#
#               La Colmena Labs.
#
# Copyright (c) 2012 Miranda Leiva, Martín Alejandro.
# E-mail: debianitram (at) gmail.com
#
# License Code:
# License Content:

# Importando paquetes #
from gluon.storage import Storage
from gluon import current
from cliente import cliente
from prestamo import prestamo, concepto_prestamo
from cuota import cuota


class Container(object):

    def __init__(self, config):
        super(Container, self).__init__()
        self.env = Storage(current.globalenv)
        self.db = self.env.get('db')
        self.auth = self.env.get('auth')
        self.config = config

    # Definición de los módulos #
    #
    def load(self):
        ''' Prestamos '''
        if not hasattr(self, 'cliente'):
            self.cliente = cliente(self)

        if not hasattr(self, 'concepto_prestamo'):
            self.concepto_prestamo = concepto_prestamo(self) 

        if not hasattr(self, 'prestamo'):
            self.prestamo = prestamo(self)

        if not hasattr(self, 'cuota'):
            self.cuota = cuota(self)

    # Definición de las tablas #
    #
    def define_tables(self):
        ''' Definición de las tablas para Prestamos '''
        if not hasattr(self.db, self.cliente.name_table):
            self.cliente.define_tables()

        if not hasattr(self.db, self.prestamo.name_table):
            self.concepto_prestamo.define_tables()
            self.prestamo.define_tables()

        if not hasattr(self.db, self.cuota.name_table):
            self.cuota.define_tables()