from django.shortcuts import render
from perfil.models import Conta, Categoria
from perfil.utils import calcula_porcentagem
from extrato.models import valores
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from perfil.utils import calcula_total
import json
from datetime import datetime

# Create your views here.
def definir_planejamento(request):
    categorias = Categoria.objects.all()
    
    return render(request, 'definir_planejamento.html', {'categorias': categorias})

@csrf_exempt
def update_valor_categoria(request, id):
    novo_valor = json.load(request)['novo_valor']
    categoria = Categoria.objects.get(id=id)
    categoria.valor_planejamento = novo_valor
    categoria.save()
    return JsonResponse({'Status': 'Sucesso'})

def ver_planejamento(request):
    categorias = Categoria.objects.all()
    Valores = valores.objects.filter(data__month = datetime.now().month).filter(tipo="S")

    total_gasto = calcula_total(Valores, 'valor')
    total_planejamento = calcula_total(categorias, 'valor_planejamento')

    percentual_gasto = calcula_porcentagem(total_gasto, total_planejamento)   
    

    return render(request, 'ver_planejamento.html',{'categorias': categorias, 'total_gasto': total_gasto, 'total_planejamento': total_planejamento, 'percentual_gasto': percentual_gasto})
