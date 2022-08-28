# INF2102 - PROJETO FINAL DE PROGRAMACAO - 2022.1 - 3WA

Autora: Mariana Salgueiro

# Quem@PUC

Neste repositório se encontra o Projeto Final de Programação que implementa um buscador de professores/pesquisadores da PUC-Rio. A ideia do sistema é permitir identificar os professores/pesquisadores envolvidos com disciplinas, projetos de pesquisa e/ou desenvolvimento e as competências existentes em laboratórios e departamentos da universidade correspondentes a determinada palavra-chave.

O projeto é um sistema web construído através da linguagem de programação Python, do microframework Flask, do banco de dados de grafo AllegroGraph e do banco de dados relacional PostgreSQL.

A seguir seguem as instruções para rodar este projeto.

## Instalação do Flask

Todos os comandos devem ser executados na linha de comando ou na linha de comando do anaconda (Windows).
Todos os comandos devem ser executados dentro da pasta do projeto, salvo indicação do contrário.

### Environment 
#### Create 
```
conda create --name quempuc python
```

#### Activate
Linux:
```
source activate quempuc
```

Windows:
```
conda activate quempuc
```

### Instalação de pacotes necessários (após ativação do environment)
```
pip install -r /docs/requirements.txt
```

## Instalação e ativação do AllegroGraph (feito somente na primeira vez)
A instalação do AllegroGraph 7.0.3 foi feita no ambiente Ubuntu 18.04.6 LTS.

### Instalação no ambiente
```
curl -O https://franz.com/ftp/pri/acl/ag/ag7.0.3/linuxamd64.64/agraph-7.0.3-linuxamd64.64.tar.gz
tar zxf agraph-7.0.3-linuxamd64.64.tar.gz 
```

Esse passo cria o diretório "agraph-7.0.3".

```
agraph-7.0.3/install-agraph <caminho>/ag-7.0.3
```

### Subindo o banco de dados
Você pode iniciar o AllegroGraph executando:
```
/home/joe/tmp/ag7.3.0/bin/agraph-control --config <caminho>/ag7.3.0/lib/agraph.cfg start  
```

Você pode parar o AllegroGraph executando:  
```
/home/joe/tmp/ag7.3.0/bin/agraph-control --config <caminho>/ag7.3.0/lib/agraph.cfg stop
```

### Verificando se o AllegroGraph está executando:
Abra um navegador e entre na URL do AllegroGraph WebView:
http://localhost:10035


## Instalação e ativação do PostgreSQL (feito somente na primeira vez)
A instalação do PostgreSQL foi feita no ambiente Ubuntu 18.04.6 LTS.

```
sudo apt-get -y install postgresql
```

Checando se postgres está no ar:
```
/etc/init.d/postgresql status
```

Caso queira restartar o postgres:
```
sudo service postgresql restart
```

### Criação das tabelas no BD PostgreSQL
Aplicar os comandos do arquivo ddl localizado em: /docs/ddl.sql

## Configuração de variáveis de ambiente
Linux:
```
EXPORT FLASK_APP=run.py
EXPORT FLASK_CONFIG=development
EXPORT AGRAPH_HOST=conexao
EXPORT AGRAPH_PORT=porta
EXPORT AGRAPH_USER=user
EXPORT AGRAPH_PASSWORD=password
EXPORT POSTGRES_CONNECTION=conexao
EXPORT POSTGRES_PASSWORD=senha
EXPORT USER_DATABASE=nome_banco
```

Windows:
```
SET FLASK_APP=run.py
SET FLASK_CONFIG=development
SET AGRAPH_HOST=localhost
SET AGRAPH_PORT=porta
SET AGRAPH_USER=user
SET AGRAPH_PASSWORD=password
SET POSTGRES_CONNECTION=conexao
SET POSTGRES_PASSWORD=senha
SET USER_DATABASE=nome_banco
```

## Subir o site:
```
flask run
```

Acessar http://localhost:5000/ no browser.