@auth.requires_signature()
def deudas_cliente():
    prestamo = container.prestamo
    cliente_id = request.args(-1)
    grid = prestamo.resumen_deudas(cliente_id)
    return dict(grid=grid)



@auth.requires_signature()
def detalle_prestamo():
    prestamo = container.prestamo
    return prestamo.detalle(request.vars.pid)



@auth.requires_signature()
def cancelar_prestamo():
    prestamo = container.prestamo
    cuota = container.cuota
    prestamo_id = request.vars.idprestamo
    db[prestamo.name_table](int(prestamo_id)).update_record(estado=3)
    ## Consultamos por todas las cuotas que pertenezcan a prestamo_id
    ## y que sus estados sean diferentes de 2 (pagadas).
    q = db[cuota.name_table]['prestamo_id'] == prestamo_id
    q &= db[cuota.name_table]['estado'] != 2
    db(q).update_naive(estado=4)
    db.commit()
    
    jquery = "$('#dresumen_tr_%s').hide(); $('#detalle_prestamo').html(' ');" 
    return jquery % prestamo_id



@auth.requires_signature()
def generar_prestamo():
    from modal_FieldsReference import modalFieldReference as mfr
    
    prestamo = container.prestamo
    cuota = container.cuota
    cliente_id = request.vars.get('cliente_id')

    modal = mfr(db[prestamo.name_table].concepto,
                btn_title='Agregar nuevo concepto',
                btn_icon='icon-plus-sign',
                modal_title='Nuevo | Concepto',
                modal_key=str(db[prestamo.name_table].concepto).replace('.', '_')
                )
    db[prestamo.name_table].concepto.comment = modal.btn()

    # Config fields
    cliente, f_emision = prestamo.getFields('cliente_id', 'fecha')
    cliente.default = cliente_id
    cliente.writable = False
    f_emision.default = request.now.date()

    form = SQLFORM(db[prestamo.name_table])

    if form.accepts(request.vars, session):
        # Generar e insertar las cuotas en la BD
        cuota.generar(form, insert=True)
        # Creamos url de redirección
        url = URL(c='prestadmin', f='planilla_prestamo', 
                  args=[form.vars.id],
                  user_signature=True, extension=False)
        
        redirect(url, client_side=True)
    
    return dict(form=form, modal=modal.modal())



@auth.requires_signature()
def planilla_prestamo():
    from StringIO import StringIO
    from reporte.planilla_control import planilla_control
    from gluon.contenttype import contenttype

    out = StringIO()
    report = planilla_control(out, request.args(-1))
    report.render()
    data = out.getvalue()
    out.close()
    response.headers['Content-Type'] = contenttype('.pdf')
    return data



@auth.requires_login()
def conceptos():
    concepto = container.concepto_prestamo

    fields = concepto.getFields('nombre', 'descripcion')
    query = concepto.search('id', 'greater', get_query=True)

    grid = SQLFORM.grid(query,
                        fields=fields,
                        maxtextlength=50,
                        csv=False,
                        editable=False,
                        ondelete=concepto.hide_record)

    # Change class for buttons submit.
    if grid.element('input', _type='submit'):
        grid.element('input', _type='submit')['_class'] = 'btn btn-success'

    return dict(grid=grid)