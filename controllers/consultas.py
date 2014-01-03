@auth.requires_login()
def caja_diaria():

    form = SQLFORM.factory(
                    Field('fecha', 'date',
                          requires=IS_NOT_EMPTY()),
                    _method='GET')
    form.custom.widget.fecha['hideerror'] = True
    form.custom.widget.fecha['_placeholder'] = 'Seleccione una fecha'

    results = {}

    if form.accepts(request.vars, session):
        fecha = request.vars.fecha
        results = container.cuota.reporte_diario(fecha)

    elif request.vars.fecha:
        fecha = request.vars.fecha
        results = container.cuota.reporte_diario(fecha)

    return dict(form=form, results=results)


@auth.requires_login()
def cuotas_cobradas():

    cuota = container.cuota
    cliente = container.cliente

    dbcuota = db[cuota.name_table]
    
    form = SQLFORM.factory(
                    Field('desde', 'date', requires=IS_NOT_EMPTY()),
                    Field('hasta', 'date', requires=IS_NOT_EMPTY()),
                    _method='GET')
    form.custom.widget.desde['hideerror'] = True
    form.custom.widget.hasta['hideerror'] = True

    results = ''
    accepts = False

    if form.accepts(request.vars, session):
        accepts = True
        desde, hasta = form.vars.desde, form.vars.hasta
        fields = cuota.getFields('id', 
                                 'nro',
                                 'fecha_pago',
                                 'prestamo_id',
                                 'valor_cuota')

        q = dbcuota.fecha_pago >= desde
        q &= dbcuota.fecha_pago <= hasta

        results = db(q).select(*fields, orderby=dbcuota.fecha_pago)

    return dict(form=form, results=results, accepts=accepts)


@auth.requires_login()
def imprimir_cc():
    # Imprimir Reporte Cuotas Cobradas.
    from StringIO import StringIO
    from reporte.cuotas_cobradas import cuotas_cobradas
    from gluon.contenttype import contenttype

    out = StringIO()
    report = cuotas_cobradas(out, **request.vars)
    report.render()
    data = out.getvalue()
    out.close()
    response.headers['Content-Type'] = contenttype('.pdf')
    return data

    