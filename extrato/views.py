from django.shortcuts import render, redirect
from perfil.models import Categoria, Conta
from .models import valores
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.template.loader import render_to_string
import os
from django.conf import settings
from weasyprint import HTML
from io import BytesIO

# Create your views here.
def novo_valor(request):
    if request.method == 'GET':
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == 'POST':
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        if len(valor.strip()) == 0 or len(descricao.strip()) == 0 or len(data.strip()) == 0 or tipo == None:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return redirect('/extrato/novo_valor')
        else:
            cadastra_valor = valores(valor = valor, categoria_id = categoria, descricao = descricao, data = data, conta_id = conta, tipo = tipo)
            cadastra_valor.save()
            conta = Conta.objects.get(id = conta)
            if tipo == 'E':
                conta.valor += float(valor)
                conta.save()
                messages.add_message(request, constants.SUCCESS, 'Entrada cadastrada com sucesso.')
            elif tipo == 'S':
                conta.valor-= float(valor)
                conta.save()
                messages.add_message(request, constants.SUCCESS, 'Saída cadastrada com sucesso.')
            return redirect('/extrato/novo_valor')

def view_extrato(request):

    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    periodo_get = request.GET.get('periodo')

    Valores = valores.objects.filter(data__month=datetime.now().month)

    if conta_get:
        Valores = Valores.filter(conta__id=conta_get)
    if categoria_get:
        Valores = Valores.filter(categoria__id= categoria_get)
    if periodo_get:
        Valores = Valores.filter(data__=periodo_get)
    #TODO: Faça um botão para limpar os filtros
    #TODO: Filtrar por período
    return render(request, 'view_extrato.html', {'Valores': Valores, 'contas': contas, 'categorias': categorias})

def exportar_pdf(request):
    Valores = valores.objects.filter(data__month=datetime.now().month)
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    template_render = render_to_string(path_template, {'Valores': Valores})
    
    path_output = BytesIO()

    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)

    return FileResponse(path_output, filename='extrato.pdf')