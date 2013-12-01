#-*- encoding:utf-8 -*-
# Módulo:
# Site: http://colmenalabs.com.ar
#
#                Colmena Labs (c) 2013.
#
# Programmer: Miranda Leiva, Martín Alejandro.
# E-mail: debianitram (at) gmail.com
#

from gluon.http import redirect, HTTP
from gluon.html import URL


class objbase(object):

    def __init__(self, container):
        self.container = container
        self.migrate = True
        self.name_table = self.__class__.__name__
        self.format = ''

    def define_tables(self):
        pass

    def setLabels(self, dbconf):
        pass

    def setReadableAndWritable(self, dbconf):
        dbconf.id.readable, dbconf.id.writable = (False, False)

    def setRequires(self, dbconf):
        pass

    def setRepresent(self, dbconf):
        pass

    # Controles.
    def style2field(self, field, style):
        ''' Dar formato a los widget para los formularios '''
        return ('#%s{%s}' % (str(field).replace('.', '_'), style),
                '#%s__error{%s}' % (str(field).split('.')[1], style))

    def getFields(self, *fields):
        db = self.container.db
        return [db[self.name_table][field] for field in fields]

    def hide_record(self, table, record):
        # Control para desactivar los registros.
        db = self.container.db
        db[table](record).update_record(is_active=False)
        db.commit()
        

    def search(self, field, operator, value=0, **kwgs):
        db = self.container.db
        table = db[self.name_table]
        fields = kwgs.get('fields', None)  # List of field/s
        limitby = kwgs.get('limitby', None)
        orderby = kwgs.get('orderby', None)
        cache = kwgs.get('cache', None)
        cacheable = kwgs.get('cacheable', False)
        getQuery = kwgs.get('get_query', None)
        getSet = kwgs.get('get_set', None)

        if operator == 'equal':
            q = (table[field] == value) & (table.is_active != False)
        elif operator == 'distinct':
            q = (table[field] != value) & (table.is_active != False)
        elif operator == 'greater':
            q = (table[field] > value) & (table.is_active != False)
        elif operator == 'contains':
            q = table[field].lower().contains(value.lower())
        elif operator == 'query' and field == 'query':
            q = value

        if getQuery:
            return q
        elif getSet:
            return db(q)
        elif fields:
            return db(q).select(*fields,
                                 limitby=limitby,
                                 orderby=orderby,
                                 cache=cache,
                                 cacheable=cachable)
        else:
            return db(q).select(limitby=limitby,
                                orderby=orderby,
                                cache=cache,
                                cacheable=cacheable)
