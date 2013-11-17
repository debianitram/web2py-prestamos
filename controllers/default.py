# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():    
    cuota = container.cuota
    cliente = container.cliente
    tbcuota = db[cuota.name_table]

    if request.vars.get('redirect', False):
        cliente_id = request.vars.get('cliente')
        response.js = "$('.tabbable li:eq(1) a').tab('show')"
        redirect(URL('clientes', 'index',
                args=('view', cliente.name_table, cliente_id),
                user_signature=True))

    # DISEÑO DE LA GRILLA.
    ui= dict(widget='table',
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

    fields = cuota.getFields('prestamo_id',
                             'nro',
                             'valor_cuota',
                             'fecha_limite',
                             'estado')

    # REPRESENTACIÓN DE CAMPOS
    fields[0].represent = lambda value, row: \
                          A(cliente.get_name(value.cliente_id), \
                            _href=URL(vars=dict(cliente=value.cliente_id, \
                                                prestamo=value.id,
                                                redirect=True), \
                                      user_signature=True))
    fields[1].represent = lambda value, row: \
                          SPAN('ID: %s -> Cuota: %s' % (row.prestamo_id, value))
    fields[2].represent = lambda value, row: SPAN('$ ', value)
    fields[3].represent = lambda value, row: SPAN(value, _style='color:red') \
                          if value == request.now.date() else value

    # ENCABEZADOS
    headers = {str(fields[0]): 'Cliente',
               str(fields[1]): 'ID Prestamos -> Nº Cuota',
               str(fields[2]): 'Importe'}

    # LONGITUD DEL TEXTO EN LOS CAMPOS DE LA TABLA.
    maxtextlengths = {str(fields[0]): 35,
                      str(fields[1]): 20,
                      str(fields[2]): 20}


    # CONSULTA.
    q = tbcuota.estado.belongs(1, 3)
    q &= tbcuota.fecha_limite <= request.now.date()

    grid = SQLFORM.grid(q,
                        fields=fields,
                        orderby=fields[-2],
                        ui=ui,
                        headers=headers,
                        maxtextlengths=maxtextlengths,
                        csv=False,
                        searchable=False,
                        create=False,
                        details=False,
                        editable=False,
                        deletable=False,)
    
    return dict(grid=grid)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
