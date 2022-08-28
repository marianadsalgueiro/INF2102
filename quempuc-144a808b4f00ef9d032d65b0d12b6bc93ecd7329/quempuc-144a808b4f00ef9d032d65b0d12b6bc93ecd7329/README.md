# INF2102 - PROJETO FINAL DE PROGRAMACAO - 2022.1 - 3WA

Autora: Mariana Salgueiro

# Quem@PUC

Neste repositório se encontra o Projeto Final de Programação que implementa um buscador de professores/pesquisadores da PUC-Rio. A ideia do sistema é permitir identificar os professores/pesquisadores envolvidos com disciplinas, projetos de pesquisa e/ou desenvolvimento e as competências existentes em laboratórios e departamentos da universidade correspondentes a determinada palavra-chave.

O projeto é um sistema web construído através da linguagem de programação Python, do microframework Flask e do banco de dados de grafo AllegroGraph.

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
pip install -r requirements.txt
```

### Configuração de variáveis de ambiente

Linux:
```
export FLASK_APP=run.py
export FLASK_CONFIG=development
```

Windows:
```
SET FLASK_APP=run.py
SET FLASK_CONFIG=development
```

### Subir o site:
```
flask run
```

SET AGRAPH_HOST=localhost
SET AGRAPH_PORT=(inserirAquiAPortaDoAllegro)
SET AGRAPH_USER=(inserirAquiOUserDoAllegro)
SET AGRAPH_PASSWORD=(inserirAquiOPasswordDoAllegro)