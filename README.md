# AIRFLOW PYTHON Demo

Seja bem vindo ao código da nossa apresentação Python. O video referente a essa apresentação pode ser encontrada diretamente no canal do youtube ou no link da apresentação que também foi salva na raiz desse repositório (Ou aqui embaixo também após a conclusão da apresentação).<br><br>


# Requisitos para deploy local do Apache Airflow

- Esse projeto essencialmente somente precisa do Docker Desktop como requisito principal para rodar localmente o Apache Airflow.
- A sua versão do docker desktop deve incluir docker-compose (verifique a documentação diretamente no site do docker para efetuar a instalação desse sistema corretamente).


# Requisitos específicos para rodar a DAG exemplo no diretório **dags/**

- Acesso a uma conta AWS com permissões para criar roles, inserir objetos no s3 e criar/publicar mensagens no SNS.
- Configurar as credênciais AWS no servidor airflow. Para isso clique no menu superior em "Admin >> Connections" e, posteriormente, clique no botão com "+" para inserir uma nova conexão. Insira no campo **Extras** o seguinte json.

```json
{"aws_access_key_id":"sua_access_key", "aws_secret_access_key": "sua_secret_key", "region_name": "region"}

```

# Como montar esse projeto localmente?

- crie o **.env** local na raiz do projeto
```bash
echo -e "AIRFFLOW_UID=$(id-u)\nAIRFLOW_GID=0" > .env
```
- Efetuar airflow init para criar usuário e demais configurações do airflow
```bash
docker-compose up airflow-init
```
- Inicializar airflow localmente
```bash
docker-compose up
```
Agora basta acessar localmente (usuario e senha padrão: **airflow** - em ambos os campos)

```bash
http://localhost:8080/
```

# Outros comandos
```bash
docker-compose down && docker-compose up
```