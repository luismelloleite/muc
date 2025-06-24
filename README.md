# Sistema de Controle de Visitantes

Sistema para controle de entrada e saída de visitantes em condomínios.

## Requisitos

- Python 3.8+
- Django 5.2
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://gitlab.ufcat.edu.br/internos/muc_portaria.git
cd muc_portaria
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

## Configuração da Base de Dados Externa

O sistema utiliza uma base de dados externa para sincronização de visitantes. Para criar esta base, configure em settings.py uma DATABASE chamada external e:

1. Execute o comando:
```bash
python manage.py migrate --database=external
```

## Sincronização manual da base de dados
```bash
python manage.py sync_visitantes --host <host> --port <port> --database <database> --user <user> --password <password>
```

## Configuração da Sincronização Automática (Windows)

Para configurar a sincronização automática no Windows:

1. Execute o comando:
```bash
python manage.py schedule_sync
```

Este comando irá:
- Criar um arquivo batch `sync_visitantes.bat` no diretório raiz
- Criar uma tarefa agendada no Windows que executa a sincronização diariamente à meia-noite
- A tarefa será executada com privilégios de sistema

Para verificar ou modificar a tarefa agendada:
1. Abra o "Agendador de Tarefas" do Windows
2. Procure por "Sincronização de Visitantes"
3. Você pode modificar o agendamento conforme necessário
4. Alternativamente, utilize o comando abaixo para verificar se está em execução o serviço:
```bash
schtasks /query /tn "Sincronização de Visitantes"
```
5. Para remover, utilize:
```bash
schtasks /delete /tn "Sincronização de Visitantes" /f
```

## Uso

1. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

2. Acesse o sistema em `http://localhost:8000`

3. Faça login com as credenciais do superusuário criado

## Funcionalidades

- Cadastro de visitantes
- Controle de entrada e saída
- Geração de relatórios
- Sincronização com base de dados externa
- Gerenciamento de usuários
- Interface responsiva

## Estrutura do Projeto

```
portaria_muc/
├── manage.py
├── requirements.txt
├── portaria_muc/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── visitantes/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    └── templates/
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 