from django.core.management.base import BaseCommand
from visitantes.models import Visitante
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Popula o banco de dados com visitantes fictícios'

    def handle(self, *args, **kwargs):
        # Listas de dados fictícios
        nomes = [
            'João Silva', 'Maria Santos', 'Pedro Oliveira', 'Ana Costa', 'Carlos Pereira',
            'Juliana Lima', 'Lucas Souza', 'Mariana Ferreira', 'Rafael Almeida', 'Beatriz Carvalho',
            'Gabriel Martins', 'Isabela Rodrigues', 'Thiago Santos', 'Laura Oliveira', 'Felipe Costa',
            'Amanda Pereira', 'Bruno Lima', 'Carolina Souza', 'Daniel Ferreira', 'Eduarda Almeida'
        ]
        
        sobrenomes = [
            'Silva', 'Santos', 'Oliveira', 'Costa', 'Pereira', 'Lima', 'Souza', 'Ferreira',
            'Almeida', 'Carvalho', 'Martins', 'Rodrigues', 'Gomes', 'Ribeiro', 'Fernandes'
        ]
        
        tipos_documento = ['CPF', 'RG', 'CNH']
        blocos = ['A', 'B', 'C', 'D', 'E']
        marcas_veiculos = ['Toyota', 'Honda', 'Volkswagen', 'Fiat', 'Chevrolet', 'Ford', 'Hyundai']
        modelos_veiculos = ['Corolla', 'Civic', 'Gol', 'Uno', 'Onix', 'Ka', 'HB20']
        cores_veiculos = ['Preto', 'Branco', 'Prata', 'Vermelho', 'Azul', 'Cinza']

        # Gerar 80 visitantes
        for i in range(80):
            # Gerar nome completo aleatório
            nome = random.choice(nomes)
            sobrenome = random.choice(sobrenomes)
            nome_completo = f"{nome} {sobrenome}"

            # Gerar número de documento aleatório
            tipo_doc = random.choice(tipos_documento)
            if tipo_doc == 'CPF':
                numero_doc = ''.join([str(random.randint(0, 9)) for _ in range(11)])
            else:
                numero_doc = ''.join([str(random.randint(0, 9)) for _ in range(9)])

            # Gerar dados do veículo (50% de chance de ter veículo)
            tem_veiculo = random.choice([True, False])
            placa = None
            marca = None
            modelo = None
            cor = None
            
            if tem_veiculo:
                letras = ''.join([chr(random.randint(65, 90)) for _ in range(3)])
                numeros = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                placa = f"{letras}{numeros}"
                marca = random.choice(marcas_veiculos)
                modelo = random.choice(modelos_veiculos)
                cor = random.choice(cores_veiculos)

            # Gerar horário de entrada (últimos 30 dias)
            dias_aleatorios = random.randint(0, 30)
            horario_entrada = timezone.now() - timedelta(days=dias_aleatorios)

            # Criar visitante
            Visitante.objects.create(
                nome_completo=nome_completo,
                tipo_documento=tipo_doc,
                numero_documento=numero_doc,
                bloco=random.choice(blocos),
                apartamento=str(random.randint(101, 999)),
                placa_veiculo=placa,
                marca_veiculo=marca,
                modelo_veiculo=modelo,
                cor_veiculo=cor,
                horario_entrada=horario_entrada
            )

        self.stdout.write(self.style.SUCCESS('80 visitantes fictícios foram criados com sucesso!')) 