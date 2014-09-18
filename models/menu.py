# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Colmena Labs'),XML('&trade;&nbsp;'),
                  _class="brand",_href="http://colmenalabs.com.ar/")
response.title = 'Cambios para el curso de web2py'
response.subtitle = 'Villa Parque - ver. 1.0'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Martín Miranda <debianitram@gmail.com>'
response.meta.description = 'Sistema de Prestamos - Villa Parque'
response.meta.keywords = 'Colmena Labs - Soluciones Tecnológicas'
response.meta.generator = 'Colmena Labs - Soluciones Tecnológicas'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################
app = request.application
ctr = request.controller

response.menu = [
    (SPAN(I(_class='icon-white icon-list-alt'), ' Menu', _style='color:yellow'),
        False, None,[
          (SPAN(I(_class='icon-home'), ' Inicio'),
           False,
           URL('default', 'index')),
           LI(_class="divider"),
          (SPAN(I(_class='icon-user'), ' Clientes'), 
           False,
           URL('clientes', 'index')
           ),
          (SPAN(I(_class='icon-align-justify'), ' Conceptos'), 
           False,
           URL('prestadmin', 'conceptos')
           ),
          (SPAN(I(_class='icon-filter'), ' Consultas'), False, None, [
            ('Consulta diaria', 
              False,
              URL(c='consultas', f='caja_diaria', user_signature=True)
            ),
            ('Cuotas cobradas',
              False,
              URL(c='consultas', f='cuotas_cobradas', user_signature=True)
            ),
            ('Resumen de créditos',
              False,
              URL(c='consultas', f='resumen_creditos', user_signature=True)
            )]),
          LI(_class='divider'),
          (SPAN('Admin'), False, None, [
            ('Interfaz administrativa',
              False,
              URL('admin', 'default', 'design/%s' % app)
            ),
            ('Base de datos',
              False,
              URL(app, 'appadmin', 'index'))]
        )
          ])
]

if "auth" in locals(): auth.wikimenu() 
