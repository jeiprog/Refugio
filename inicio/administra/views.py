from django.shortcuts import render, redirect
from administra.models import Mascota
from django.core.paginator import Paginator
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Mascota

def base(request):
    return render(request, 'base.html')


def mas(request):
    masc = Mascota.objects.all()
    paginator = Paginator(masc, 5)
    pagina = request.GET.get("page") or 1
    lista = paginator.get_page(pagina)
    pagina_actual = int(pagina)
    paginas = range(1, lista.paginator.num_pages + 1)
    return render(request, 'mascotas_registradas.html', {'mascotas': lista, 'paginas': paginas, 'pagina_actual': pagina_actual})


def excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Mascotas"

    ws.append(['ID', 'Nombre', 'Edad', 'Género', 'Raza', 'Descripción', 'Fecha de creación'])

    mascotas = Mascota.objects.all()

    for mascota in mascotas:
        ws.append([
            mascota.id,
            mascota.nombre,
            mascota.edad,
            mascota.genero,
            mascota.raza,
            mascota.descripcion,
            mascota.created.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mascotas.xlsx'
    
    wb.save(response)
    return response
