@auth.requires_login()
def index():

    cliente = container.cliente
    prestamo = container.prestamo

    query = cliente.search('id', 'greater', get_query=True)
    fields = cliente.getFields('nombre', 
                               'apellido',
                               'dni',
                               'tipo_cliente',
                               'movil')

    if 'view' in request.args:
        cliente.getFields('id')[0].readable = True

    grid = SQLFORM.grid(query,
                        fields=fields,
                        csv=False,
                        ui=cliente.ui_grid(),
                        oncreate=cliente.oncreate,
                        ondelete=cliente.hide_record)
    # Change class for buttons submit.
    if grid.element('input', _type='submit'):
        grid.element('input', _type='submit')['_class'] = 'btn btn-success'
    
    return dict(grid=grid)
