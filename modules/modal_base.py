#!/usr/bin/env python
#-*- encoding:utf-8 -*-


# Modal base.

from gluon import current
from gluon.html import DIV, A, I, H3, BUTTON
from gluon.http import HTTP
from gluon.compileapp import LOAD


class ModalBase(object):

    def __init__(self, **attr):
        self.auth = current.globalenv.get('auth', None)

        # Config Modal.
        self.btn_title = attr.get("btn_title", "Titulo botón")
        self.btn_name = attr.get("btn_name", "")
        self.btn_icon = attr.get("btn_icon", "icon-minus")
        self.btn_class = attr.get("btn_class", "")
        self.modal_title = attr.get("modal_title", "Titulo Modal")
        self.modal_key = attr.get("modal_key", self.__class__.__name__)
        self.modal_id = attr.get("modal_id", "id_%s" % self.modal_key)
        self.modal_target = "target_%s" % self.modal_id

    def btn(self):
        btn = A(I(_class=self.btn_icon),
                self.btn_name,
                **{"_role": "button",
                   "_class": self.btn_class,
                   "_data-toggle": "modal",
                   "_href": "#%s" % self.modal_id,
                   "_title": self.btn_title})
        return btn

    def window(self, content):
        div_modal = DIV(
                        DIV(
                            H3(self.modal_title, _id="myModalLabel"),
                            _class="modal-header"),
                        DIV(content, _class="modal-body"),
                        DIV(
                            BUTTON("Cerrar", **{"_class": "btn btn-primary",
                                                "_data-dismiss": "modal",
                                                "_aria-hidden": "true"}),
                            _class="modal-footer",
                            ),
                        **{"_id": "%s" % self.modal_id,
                           "_class": "modal hide face",
                           "_tabindex": "-1",
                           "_role": "dialog",
                           "_aria-hidden": "true",
                           "_aria-labelledby": "myModalLabel"}
                    )
        return div_modal

    def content(self):
        # Debe definirse este método.
        raise NotImplementedError

    def modal(self):
        if current.request.get_vars._ajax_add == self.modal_key:
            raise HTTP(200, self.content())

        return self.window(LOAD(current.request.controller,
                                current.request.function,
                                args=current.request.args,
                                vars=dict(_ajax_add=self.modal_key),
                                target=self.modal_target,
                                ajax=True)
                                )