#-*- encoding:utf-8 -*-
#
# SAISE. Sistema Administrativo Integrador & Seguimiento de Expedientes.
# Módulo: {Nombre del módulo}
# Site: http://colmenalabs.com.ar
#
#                   La Colmena Labs.
#
# Copyright (c) 2013 Miranda Leiva, Martín Alejandro.
# E-mail: debianitram (at) gmail.com
#
# License Code:
# License Content:

# Importando paquetes.
import os
from gluon.storage import Storage

# Quitar estás líneas una vez finalizado el proyecto.
if request.is_local:
    from gluon.custom_import import track_changes
    track_changes()

### Config App.
config = Storage()
# Extra
config.get_name_of = lambda user: "%(last_name)s, %(first_name)s" % user
config.client_name = lambda row: "%(apellido)s, %(nombre)s" % row
config.app_installed = False
