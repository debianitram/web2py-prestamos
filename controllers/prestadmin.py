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
    
    return "$('#dresumen_tr_%s').hide(); $('#detalle_prestamo').html(' ');" % prestamo_id

@auth.requires_signature()
def generar_prestamo():
    prestamo = container.prestamo
    cuota = container.cuota
    cliente_id = request.vars.get('cliente_id')

    # Config fields
    cliente, f_emision = prestamo.getFields('cliente_id', 'fecha')
    cliente.default = cliente_id
    cliente.writable = False
    f_emision.default = request.now.date()

    form = SQLFORM(db[prestamo.name_table])

    if form.accepts(request.vars, session):
        session.flash = "Se generó el prestamo exitosamente"
        
        # Generar e insertar las cuotas en la BD
        cuota.generar(form, insert=True)
        # Redireccionamos
        url = URL(c='clientes', f='index', 
                  args=['view', 'cliente', cliente_id],
                  user_signature=True, extension=False)
        
        redirect(url, client_side=True)
    
    return dict(form=form)