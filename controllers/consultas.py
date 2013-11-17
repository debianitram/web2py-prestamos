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

    