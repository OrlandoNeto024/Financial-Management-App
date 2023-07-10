from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta, Categoria
from contas.models import ContaPaga, ContaPagar
from extrato.models import valores
from django.contrib import messages
from django.contrib.messages import constants
from .utils import calcula_total, calcula_equilibrio_financeiro
from datetime import datetime
# Create your views here.

def home(request):
    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')

    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day

    conta = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = conta.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    contas_proximas_vencimento = conta.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)

    total_contas_vencidas = len(contas_vencidas)
    total_contas_proximas_vencimento = len(contas_proximas_vencimento)

    Valores = valores.objects.filter(data__month=datetime.now().month)
    entradas = Valores.filter(tipo='E')
    saidas = Valores.filter(tipo='S')
    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')
    
    despesa = ContaPagar.objects.all()
    despesa_mensal = calcula_total(despesa, 'valor')

    total_livre = total_entradas - despesa_mensal

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    return render(request, 'home.html', {'contas': contas, 'total_contas': total_contas, 'total_contas_vencidas': total_contas_vencidas, 'total_contas_proximas_vencimento': total_contas_proximas_vencimento, 'total_entradas': total_entradas, 'total_saidas': total_saidas, 'percentual_gastos_essenciais': int(percentual_gastos_essenciais), 'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais), 'despesa_mensal': despesa_mensal, 'total_livre': total_livre})

def gerenciar(request):
    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')

    categorias = Categoria.objects.all()

    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas': total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
        return redirect('/perfil/gerenciar')
    else:
        conta = Conta(apelido=apelido, banco=banco, tipo=tipo, valor=f'{valor}', icone=icone)
        conta.save()
        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso.')

    return redirect('/perfil/gerenciar')

def deletar_banco(request, id):
    conta = Conta.objects.get(id = id)
    conta.delete()
    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso.')

    return redirect('/perfil/gerenciar')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria').capitalize()
    essencial = bool(request.POST.get('essencial'))

    if len(nome.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha o campo de categoria.')
    else:
        categoria = Categoria(categoria=nome, essencial=essencial)
        categoria.save()
        messages.add_message(request, constants.SUCCESS, 'Categoria adicionada com sucesso.')

    return redirect('/perfil/gerenciar')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id = id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()
    
    for categoria in categorias:
        Valores = valores.objects.filter(categoria=categoria)
        total = 0
        
        for v in Valores:
            total = total + v.valor
        dados[categoria.categoria] = total

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})

    
    