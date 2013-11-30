@auth.requires_signature()
def preview():
    cuota = container.cuota
    return cuota.generar(request, insert=False)


@auth.requires_signature()
def abonar_cuota():
    from decimal import Decimal
    idcuota = request.vars.get('idcuota')
    total_pago = Decimal(request.vars.get('pago'))
    total_debe = Decimal(request.vars.get('debe'))
    prestamo = container.prestamo
    tbcuota = db[container.cuota.name_table]
    tbprestamo = db[prestamo.name_table]

    
    c = tbcuota(idcuota)
    c.update_record(fecha_pago=request.now.date(), estado=2)

    # Incrementar Total Pagó - Decrementar Total Debe.
    total_pago += c.valor_cuota
    total_debe -= c.valor_cuota
    
    q = db((tbcuota.prestamo_id == c.prestamo_id) & (tbcuota.estado != 2))
    if q.count() == 0:
        # Si los estados de cuotas del prestamo son distintas de 2
        # cambiamos el estado del prestamo a finalizado.
        tbprestamo(c.prestamo_id).update_record(estado=2)
        db.commit()
        message = 'Finalizó el crédito: %s exitosamente' % c.prestamo_id
        session.flash = message
        redirect(URL('clientes', 'index',
                    args=['view', 'cliente', c.prestamo_id.cliente_id],
                    user_signature=True,
                    extension=False), client_side=True)
    else:
        tags = TAG[''](TD(c.nro), 
                       TD("$%.2f" % c.valor_cuota),
                       TD(c.fecha_limite),
                       TD(SPAN('pagada', _class='label label-success')),
                       TD(c.fecha_pago),
                       TD(''))
    
    db.commit()
    js = "jQuery('#tr_cuota_%s').html('%s'); " % (idcuota, tags)
    js += "jQuery('#ttpago').html('%s'); " % total_pago
    js += " jQuery('#ttdebe').html('%s');" % total_debe
    return js
