#-*- encoding:utf-8 -*-
# debianitram (at) colmenalabs.com.ar

from .modal_base import ModalBase
from gluon import current
from gluon.html import TAG, OPTION
from gluon.sqlhtml import SQLFORM


class modalFieldReference(ModalBase):
    """autocomplete es None o el nombre del campo representativo del form"""

    def __init__(self, field, autocomplete=None, **kargs):
        ModalBase.__init__(self, **kargs)

        self.field = field
        self.autocomplete = autocomplete

        if not self.field.type.startswith('reference'):
            raise SyntaxError("Sólo puede ser usado con campos referenciados")
        if not hasattr(self.field.requires, 'options'):
            raise SyntaxError("No pueden determinarse las opciones")

    def content(self):
        formnamemodal = "form_%s" % self.modal_key
        table = self.field._db[self.field.type[10:]]
        form = SQLFORM(table, formname=formnamemodal)

        if form.accepts(current.request.vars,
                        current.session,
                        formname=formnamemodal):

            if not self.autocomplete:
                options = TAG[''](*[OPTION(v,
                                _value=k,
                                _selected=str(form.vars.id) == str(k))
                                for (k, v) in self.field.requires.options()])
                _cmd = "jQuery('#%s').html('%s');"
                _cmd += "jQuery('#%s').modal('hide')"
                command = _cmd % (self.modal_key,
                                  options.xml().replace("'", "\'"),
                                  self.modal_id)
            else:
                fieldtarget = str(table[self.autocomplete]).replace('.', '_')
                _cmd = "jQuery('#%(modal_key)s').val('%(autocomplete)s');"
                _cmd += "jQuery('#_autocomplete_%(ftarget)s_auto').val(%(id)s);"
                _cmd += "jQuery('#%(modal_id)s').modal('hide');"

                command = _cmd % dict(modal_key=self.modal_key,
                                      autocomplete=form.vars[self.autocomplete],
                                      id=form.vars.id,
                                      ftarget=fieldtarget,
                                      modal_id=self.modal_id)

            current.response.flash = "Se creó el registro"
            current.response.js = command

        elif form.errors:
            current.response.flash = "Controle el formulario"

        return form