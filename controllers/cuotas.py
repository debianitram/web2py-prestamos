@auth.requires_signature()
def preview():
    cuota = container.cuota
    return cuota.generar(request, insert=False)



@auth.requires_signature()
def abonar_cuota():
    return container.cuota.abonar(request)
