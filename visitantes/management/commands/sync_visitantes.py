from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db.utils import OperationalError as DjangoOperationalError # Renomear para evitar conflito
from visitantes.models import Visitante, LogAtividade, CustomUser # Adicionar CustomUser
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
import logging
import os # Adicionado para variáveis de ambiente
from dotenv import load_dotenv # Adicionado para carregar .env

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sincroniza os dados de visitantes e logs de atividades com um servidor PostgreSQL remoto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            help='Host do servidor PostgreSQL remoto. Pode ser definido via variável de ambiente DB_HOST.',
            default=None # Alterado de required=True
        )
        parser.add_argument(
            '--port',
            type=str,
            default='5432',
            help='Porta do servidor PostgreSQL remoto. Pode ser definido via DB_PORT. Padrão: 5432.'
        )
        parser.add_argument(
            '--database',
            type=str,
            help='Nome do banco de dados remoto. Pode ser definido via variável de ambiente DB_NAME.',
            default=None # Alterado de required=True
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Usuário do banco de dados remoto. Pode ser definido via variável de ambiente DB_USER.',
            default=None # Alterado de required=True
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do banco de dados remoto. Pode ser definido via variável de ambiente DB_PASS.',
            default=None # Alterado de required=True
        )

    def handle(self, *args, **options):
        load_dotenv() # Carrega variáveis do arquivo .env para o ambiente

        self.visitante_table_name = Visitante._meta.db_table
        self.log_atividade_table_name = LogAtividade._meta.db_table
        self.custom_user_table_name = CustomUser._meta.db_table # Adicionar nome da tabela de usuário

        # Obter parâmetros de conexão (argumentos de linha de comando têm precedência sobre .env)
        db_host = options['host'] or os.getenv('DB_HOST')
        # Para a porta, precisamos de uma lógica um pouco diferente, pois options['port'] terá '5432' como padrão.
        # Queremos que o .env sobrescreva o padrão se options['port'] não foi explicitamente passado.
        db_port_arg = options['port']
        db_port_env = os.getenv('DB_PORT')
        db_port = db_port_arg if db_port_arg != '5432' or db_port_env is None else (db_port_env or '5432')

        db_name = options['database'] or os.getenv('DB_NAME')
        db_user = options['user'] or os.getenv('DB_USER')
        db_password = options['password'] or os.getenv('DB_PASS')

        if not all([db_host, db_name, db_user, db_password]):
            raise CommandError(
                "Parâmetros de conexão incompletos. "
                "Forneça --host, --database, --user, --password "
                "ou defina DB_HOST, DB_NAME, DB_USER, DB_PASS no arquivo .env."
            )

        try:
            # Conectar ao banco de dados remoto
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            
            # Criar cursor para executar consultas
            cur = conn.cursor(cursor_factory=DictCursor)
            
            # Sincronizar Usuários PRIMEIRO
            self.sync_users(cur)

            # Sincronizar Visitantes
            self.sync_visitantes(cur)

            # Sincronizar Logs de Atividades
            self.sync_logs(cur)

            # Commit das alterações
            conn.commit()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sincronização concluída com sucesso. '
                    f'Última sincronização: {datetime.now()}'
                )
            )
            
        except (psycopg2.OperationalError, DjangoOperationalError) as e: # Capturar OperationalError do psycopg2 e do Django
            logger.error(f'Erro ao conectar ao banco de dados remoto: {str(e)}')
            self.stdout.write(
                self.style.ERROR(
                    f'Erro ao conectar ao banco de dados remoto: {str(e)}'
                )
            )
        except Exception as e:
            logger.error(f'Erro durante a sincronização: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Erro durante a sincronização: {str(e)}')
            )
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    def sync_visitantes(self, cur):
        self.stdout.write("Sincronizando Visitantes...")
        # Obter todos os visitantes (incluindo os com soft delete) para garantir que todas as alterações sejam capturadas.
        # Visitante.objects.all() -> Retorna apenas os não deletados (data_exclusao__isnull=True)
        # Visitante.all_objects.all() -> Retorna todos, incluindo os deletados.
        # Usaremos all_objects para garantir que o estado de data_exclusao seja sincronizado.
        visitantes = Visitante.all_objects.all()

        count_new = 0
        count_updated = 0

        # Sincronizar cada visitante
        for visitante in visitantes:
            usuario_ultima_acao_id = visitante.usuario_ultima_acao.id if visitante.usuario_ultima_acao else None
            # Verificar se o visitante já existe no banco remoto
            query_select_id = f"""
                SELECT id FROM {self.visitante_table_name}
                WHERE id = %s
            """
            cur.execute(query_select_id, (visitante.id,))
            
            if cur.fetchone():
                # Atualizar visitante existente
                query_update = f"""
                    UPDATE {self.visitante_table_name}
                    SET nome_completo = %s,
                        tipo_documento = %s,
                        numero_documento = %s,
                        visitado = %s,
                        bloco = %s,
                        apartamento = %s,
                        horario_entrada = %s,
                        horario_saida = %s,
                        placa_veiculo = %s,
                        marca_veiculo = %s,
                        modelo_veiculo = %s,
                        cor_veiculo = %s,
                        sincronizado = %s,
                        data_criacao = %s,
                        data_atualizacao = %s,
                        usuario_ultima_acao_id = %s,
                        data_exclusao = %s
                    WHERE id = %s
                """
                cur.execute(query_update, (
                    visitante.nome_completo,
                    visitante.tipo_documento,
                    visitante.numero_documento,
                    visitante.visitado,
                    visitante.bloco,
                    visitante.apartamento,
                    visitante.horario_entrada,
                    visitante.horario_saida,
                    visitante.placa_veiculo,
                    visitante.marca_veiculo,
                    visitante.modelo_veiculo,
                    visitante.cor_veiculo,
                    visitante.sincronizado,
                    visitante.data_criacao,
                    visitante.data_atualizacao,
                    usuario_ultima_acao_id,
                    visitante.data_exclusao,
                    visitante.id
                ))
                count_updated += 1
            else:
                # Inserir novo visitante
                query_insert = f"""
                    INSERT INTO {self.visitante_table_name} (
                        id, nome_completo, tipo_documento, numero_documento,
                        visitado, bloco, apartamento, horario_entrada, horario_saida,
                        placa_veiculo, marca_veiculo, modelo_veiculo, cor_veiculo, sincronizado,
                        data_criacao, data_atualizacao, usuario_ultima_acao_id, data_exclusao
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(query_insert, (
                    visitante.id,
                    visitante.nome_completo,
                    visitante.tipo_documento,
                    visitante.numero_documento,
                    visitante.visitado,
                    visitante.bloco,
                    visitante.apartamento,
                    visitante.horario_entrada,
                    visitante.horario_saida,
                    visitante.placa_veiculo,
                    visitante.marca_veiculo,
                    visitante.modelo_veiculo,
                    visitante.cor_veiculo,
                    visitante.sincronizado,
                    visitante.data_criacao,
                    visitante.data_atualizacao,
                    usuario_ultima_acao_id,
                    visitante.data_exclusao
                ))
                count_new += 1
        self.stdout.write(self.style.SUCCESS(f'{visitantes.count()} visitantes processados ({count_new} novos, {count_updated} atualizados).'))

    def sync_logs(self, cur):
        self.stdout.write("Sincronizando Logs de Atividades...")
        # Obter a última data de sincronização para logs do servidor remoto
        query_max_date_log = f"""
            SELECT MAX(data_hora) as ultima_sincronizacao 
            FROM {self.log_atividade_table_name}
        """
        cur.execute(query_max_date_log)
        result_log = cur.fetchone()
        remote_max_data_hora_log = None
        if result_log and result_log['ultima_sincronizacao']:
            remote_max_data_hora_log = result_log['ultima_sincronizacao']

        # Obter logs locais novos desde a última sincronização (baseado na data_hora de criação)
        logs_to_sync = LogAtividade.objects.all()
        if remote_max_data_hora_log:
            logs_to_sync = logs_to_sync.filter(
                data_hora__gt=remote_max_data_hora_log
            )

        count_new = 0
        count_skipped = 0

        # Sincronizar cada log
        for log in logs_to_sync:
            usuario_id = log.usuario.id if log.usuario else None
            # Verificar se o log já existe no banco remoto (dupla checagem)
            query_select_id_log = f"""
                SELECT id FROM {self.log_atividade_table_name}
                WHERE id = %s
            """
            cur.execute(query_select_id_log, (log.id,))

            if cur.fetchone():
                # Log com este ID já existe no remoto.
                # Logs são tipicamente imutáveis, especialmente o campo data_hora (auto_now_add).
                # Não tentaremos atualizar; apenas pulamos.
                self.stdout.write(self.style.WARNING(f"Log ID {log.id} já existe no remoto e será pulado."))
                count_skipped += 1
                continue
            else:
                # Inserir novo log
                query_insert_log = f"""
                    INSERT INTO {self.log_atividade_table_name} (
                        id, usuario_id, acao, modelo, objeto_id, descricao, data_hora
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(query_insert_log, (
                    log.id,
                    usuario_id,
                    log.acao,
                    log.modelo,
                    log.objeto_id,
                    log.descricao,
                    log.data_hora
                ))
                count_new += 1
        self.stdout.write(self.style.SUCCESS(f'{count_new} novos logs sincronizados. {count_skipped} logs pulados (já existentes).'))

    def sync_users(self, cur):
        self.stdout.write("Iniciando sincronização de usuários...")
        logger.info("Iniciando sincronização de usuários.")

        # 1. Lidar com exclusões: Deletar do remoto usuários que não existem mais localmente.
        local_user_ids = set(CustomUser.objects.values_list('id', flat=True))
        logger.debug(f"IDs de usuários locais: {local_user_ids if local_user_ids else 'Nenhum'}")

        query_select_all_remote_ids = f"SELECT id FROM {self.custom_user_table_name}"
        cur.execute(query_select_all_remote_ids)
        remote_user_ids = set(row['id'] for row in cur.fetchall())
        logger.debug(f"IDs de usuários remotos (antes da sincronização): {remote_user_ids if remote_user_ids else 'Nenhum'}")

        ids_to_delete_on_remote = remote_user_ids - local_user_ids
        deleted_count = 0
        if ids_to_delete_on_remote:
            logger.info(f"Usuários para deletar no remoto: {ids_to_delete_on_remote}")
            query_delete_user = f"DELETE FROM {self.custom_user_table_name} WHERE id = %s"
            for user_id_to_delete in ids_to_delete_on_remote:
                try:
                    logger.debug(f"Tentando deletar usuário remoto ID: {user_id_to_delete}")
                    cur.execute(query_delete_user, (user_id_to_delete,))
                    if cur.rowcount > 0:
                        deleted_count += 1
                        logger.info(f"Usuário remoto ID: {user_id_to_delete} DELETADO. Linhas afetadas: {cur.rowcount}.")
                    else:
                        logger.warning(f"DELETE para usuário remoto ID: {user_id_to_delete} não afetou linhas. Pode já ter sido deletado ou não encontrado.")
                except psycopg2.Error as e:
                    logger.error(f"Erro Psycopg2 ao DELETAR usuário remoto ID: {user_id_to_delete}: SQLSTATE {e.pgcode} - {e.pgerror}")
                    logger.exception(f"Detalhes da exceção de deleção (psycopg2) para remote_id {user_id_to_delete}:")
                    self.stdout.write(self.style.ERROR(f"Erro Psycopg2 ao DELETAR usuário remoto ID: {user_id_to_delete}: {e}"))
                except Exception as e:
                    logger.error(f"Erro genérico ao DELETAR usuário remoto ID: {user_id_to_delete}: {e}")
                    logger.exception(f"Detalhes da exceção de deleção (genérico) para remote_id {user_id_to_delete}:")
                    self.stdout.write(self.style.ERROR(f"Erro genérico ao DELETAR usuário remoto ID: {user_id_to_delete}: {e}"))
        
        # 2. Lidar com criações e atualizações
        users_to_process_local = CustomUser.objects.all()
        self.stdout.write(f"Processando {users_to_process_local.count()} usuários locais para criação/atualização...")
        logger.info(f"Processando {users_to_process_local.count()} usuários locais para criação/atualização.")
        
        updated_count = 0
        inserted_count = 0

        for user in users_to_process_local:
            logger.debug(f"Processando usuário local ID: {user.id}, Email: {user.email}, Nome: {user.get_full_name()}")
            # Verificar se o usuário já existe no banco remoto pelo ID local
            query_select_id = f"""
                SELECT id FROM {self.custom_user_table_name}
                WHERE id = %s
            """
            cur.execute(query_select_id, (user.id,))
            remote_user_by_id = cur.fetchone()
            
            if remote_user_by_id:
                logger.info(f"Usuário ID: {user.id} ({user.email}) encontrado no remoto. Tentando UPDATE.")
                # Atualizar usuário existente
                # Não atualizamos 'data_criacao' nem 'date_joined' (data de criação original) pois devem ser imutáveis.
                # 'password' já está hasheado.
                query_update = f"""
                    UPDATE {self.custom_user_table_name}
                    SET password = %s,
                        last_login = %s,
                        is_superuser = %s,
                        username = %s,
                        first_name = %s,
                        last_name = %s,
                        email = %s,
                        is_staff = %s,
                        is_active = %s,
                        nivel_acesso = %s,
                        data_atualizacao = %s
                    WHERE id = %s
                """
                params_update = (
                    user.password,
                    user.last_login,
                    user.is_superuser,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.is_staff,
                    user.is_active,
                    user.nivel_acesso,
                    user.data_atualizacao,
                    user.id
                )
                try:
                    # Log dos primeiros 11 parâmetros (todos exceto o ID no final) para evitar log excessivo se houver muitos campos
                    logger.debug(f"Executando UPDATE para ID {user.id} com params: {params_update[:-1]}...")
                    cur.execute(query_update, params_update)
                    if cur.rowcount > 0:
                        updated_count += 1
                        logger.info(f"Usuário ID: {user.id} ({user.email}) ATUALIZADO no remoto. Linhas afetadas: {cur.rowcount}.")
                    else:
                        logger.warning(f"Usuário ID: {user.id} ({user.email}) encontrado, mas UPDATE não afetou linhas (rowcount=0). Dados podem já estar sincronizados ou ID não correspondeu na UPDATE.")
                except psycopg2.Error as e:
                    logger.error(f"Erro Psycopg2 ao ATUALIZAR usuário ID: {user.id} ({user.email}): SQLSTATE {e.pgcode} - {e.pgerror}")
                    logger.exception("Detalhes da exceção de atualização (psycopg2):")
                    self.stdout.write(self.style.ERROR(f"Erro Psycopg2 ao ATUALIZAR usuário ID: {user.id} ({user.email}): {e}"))
                except Exception as e:
                    logger.error(f"Erro genérico ao ATUALIZAR usuário ID: {user.id} ({user.email}): {e}")
                    logger.exception("Detalhes da exceção de atualização (genérico):")
                    self.stdout.write(self.style.ERROR(f"Erro genérico ao ATUALIZAR usuário ID: {user.id} ({user.email}): {e}"))
            else:
                # Usuário com ID local não encontrado no remoto.
                # Pode ser um usuário genuinamente novo, ou um usuário recriado localmente
                # (novo ID local, mas username/email já existentes no remoto).
                logger.info(f"Usuário ID local: {user.id} ({user.email}) não encontrado no remoto pelo ID. Verificando por username/email...")
                
                query_select_unique_fields = f"""
                    SELECT id FROM {self.custom_user_table_name}
                    WHERE username = %s OR email = %s
                """
                cur.execute(query_select_unique_fields, (user.username, user.email))
                remote_user_by_unique_field = cur.fetchone()

                if remote_user_by_unique_field:
                    # Usuário encontrado no remoto por username ou email, mas com ID diferente.
                    # Isso indica que o usuário foi provavelmente recriado localmente.
                    # Vamos ATUALIZAR o registro remoto existente usando seu ID remoto.
                    remote_id_to_update = remote_user_by_unique_field['id']
                    logger.warning(
                        f"Usuário ID local: {user.id} ({user.email}) não encontrado por ID, "
                        f"mas um usuário com username='{user.username}' ou email='{user.email}' "
                        f"foi encontrado no remoto com ID: {remote_id_to_update}. "
                        f"Tentando UPDATE no registro remoto ID: {remote_id_to_update}."
                    )
                    
                    query_update = f"""
                        UPDATE {self.custom_user_table_name}
                        SET password = %s,
                            last_login = %s,
                            is_superuser = %s,
                            username = %s,
                            first_name = %s,
                            last_name = %s,
                            email = %s,
                            is_staff = %s,
                            is_active = %s,
                            nivel_acesso = %s,
                            data_atualizacao = %s
                        WHERE id = %s
                    """
                    params_update_existing_remote = (
                        user.password,
                        user.last_login,
                        user.is_superuser,
                        user.username, 
                        user.first_name,
                        user.last_name,
                        user.email, 
                        user.is_staff,
                        user.is_active,
                        user.nivel_acesso,
                        user.data_atualizacao,
                        remote_id_to_update # Usa o ID remoto aqui
                    )
                    try:
                        logger.debug(f"Executando UPDATE para usuário remoto ID {remote_id_to_update} (local ID {user.id}) com params: {params_update_existing_remote[:-1]}...")
                        cur.execute(query_update, params_update_existing_remote)
                        if cur.rowcount > 0:
                            updated_count += 1
                            logger.info(f"Usuário remoto ID: {remote_id_to_update} (local ID: {user.id}, email: {user.email}) ATUALIZADO no remoto. Linhas afetadas: {cur.rowcount}.")
                        else:
                            logger.warning(f"Usuário remoto ID: {remote_id_to_update} (local ID: {user.id}, email: {user.email}) encontrado, mas UPDATE não afetou linhas. Dados podem já estar sincronizados.")
                    except psycopg2.Error as e:
                        logger.error(f"Erro Psycopg2 ao ATUALIZAR usuário remoto ID: {remote_id_to_update} (local ID: {user.id}, email: {user.email}): SQLSTATE {e.pgcode} - {e.pgerror}")
                        logger.exception(f"Detalhes da exceção de atualização (psycopg2) para remote_id {remote_id_to_update}:")
                        self.stdout.write(self.style.ERROR(f"Erro Psycopg2 ao ATUALIZAR usuário remoto ID: {remote_id_to_update} ({user.email}): {e}"))
                    except Exception as e:
                        logger.error(f"Erro genérico ao ATUALIZAR usuário remoto ID: {remote_id_to_update} (local ID: {user.id}, email: {user.email}): {e}")
                        logger.exception(f"Detalhes da exceção de atualização (genérico) para remote_id {remote_id_to_update}:")
                        self.stdout.write(self.style.ERROR(f"Erro genérico ao ATUALIZAR usuário remoto ID: {remote_id_to_update} ({user.email}): {e}"))
                else:
                    # Usuário não encontrado nem por ID local, nem por username/email.
                    # Genuinamente um novo usuário. Proceder com INSERT.
                    logger.info(f"Usuário ID: {user.id} ({user.email}) não encontrado no remoto por ID, username ou email. Tentando INSERT.")
                    query_insert = f"""
                        INSERT INTO {self.custom_user_table_name} (
                            id, password, last_login, is_superuser, username, 
                            first_name, last_name, email, is_staff, is_active, 
                            date_joined, nivel_acesso, data_criacao, data_atualizacao
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params_insert = (
                        user.id, user.password, user.last_login, user.is_superuser, user.username,
                        user.first_name, user.last_name, user.email, user.is_staff, user.is_active,
                        user.date_joined, user.nivel_acesso, user.data_criacao, user.data_atualizacao
                    )
                    try:
                        logger.debug(f"Executando INSERT para ID {user.id} com params: {params_insert[:-1]}...")
                        cur.execute(query_insert, params_insert)
                        inserted_count += 1
                        logger.info(f"Usuário ID: {user.id} ({user.email}) INSERIDO no remoto. Linhas afetadas: {cur.rowcount}.")
                    except psycopg2.Error as e:
                        logger.error(f"Erro Psycopg2 ao INSERIR usuário ID: {user.id} ({user.email}): SQLSTATE {e.pgcode} - {e.pgerror}")
                        logger.exception("Detalhes da exceção de inserção (psycopg2):")
                        self.stdout.write(self.style.ERROR(f"Erro Psycopg2 ao INSERIR usuário ID: {user.id} ({user.email}): {e}"))
                    except Exception as e:
                        logger.error(f"Erro genérico ao INSERIR usuário ID: {user.id} ({user.email}): {e}")
                        logger.exception("Detalhes da exceção de inserção (genérico):")
                        self.stdout.write(self.style.ERROR(f"Erro genérico ao INSERIR usuário ID: {user.id} ({user.email}): {e}"))

        summary_msg = (
            f'Sincronização de usuários concluída. '
            f'{inserted_count} inseridos, {updated_count} atualizados, {deleted_count} deletados no remoto.'
        )
        logger.info(summary_msg)
        self.stdout.write(self.style.SUCCESS(summary_msg))