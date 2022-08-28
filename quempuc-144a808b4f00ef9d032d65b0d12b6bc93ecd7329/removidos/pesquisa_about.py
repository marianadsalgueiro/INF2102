import itertools
from typing import Union
from os import path, getenv
from json import dump

from ... import get_db, create_app
from ...models import Carregamento
from ...utils import quantidade_de_producoes_mostradas
from ... import Namespaces
from . import atualiza_status


def pega_lattes_biografia_homepage(dados):
    """
    A partir do resultado da query QUERY_STRINGS_INFOS,
        pega o id_lattes, as biografias, e as homepages, e salva no dicionario final
    :param dados: Binding sets da pesquisa do allegro
    :return dicionario com os itens "lattes", "biografias" e "homepages"
    """
    d: dict[str] = dict()
    d['lattes'] = ''
    d['homepages'] = []
    d['biografias'] = []
    # cada binding_set é na forma {id: lattes, p: tipo, o: conteudo}
    with dados:
        for binding_set in dados:
            # salvando o id_lattes se ja nao foi salvo
            if d['lattes'] == '':
                d['lattes'] = str(binding_set.getValue("id")).strip('"')

            p = str(binding_set.getValue("p"))
            conteudo = str(binding_set.getValue("o")).strip('"')

            # salvando a homepage do professor
            if p == Namespaces.HOMEPAGE.value:
                d['homepages'].append(conteudo)

            # salvando a biografia do professor
            elif p == Namespaces.BIOGRAPHY.value:
                d['biografias'].append(conteudo)

        # verificando se tem uma biografia em pt. Se tiver, remove todas as outras
        if not d['biografias']:
            return 'Nao foi encontrada biografia para o professor'

        for bio in d['biografias']:
            if bio.endswith('@pt'):
                d['biografias'] = [bio[:-4]]
                break
    return d


def pega_email_situacao_departamento(dados):
    """
    A partir do resultado da consulta da query QUERY_STRING_EMAIL_HOMEPAGE,
        retorna os emails, a situacao e o departamento do professor.
        tambem retorna uma lista de homepages que pode ser incluido na lista coletada na
        funcao pega_lattes_biografia_homepage

    :param dados: binding sets da pesquisa do allegro
    :return: dicionario contendo os itens email, situacao, departamento e homepages
    """
    d: dict[str] = dict()
    d['homepages'] = []
    d['email'] = []
    d['situacao'] = []
    d['departamento'] = []
    # cada binding_set é na forma {nome_professor_disciplina: nome, p: tipo, o: conteudo}
    with dados:
        for bs in dados:
            p = str(bs.getValue("p"))
            o = str(bs.getValue("o")).strip('"')

            # adicionando homepages
            if p == Namespaces.HOMEPAGE.value:
                d['homepages'].append(o)
            elif p == Namespaces.MBOX.value:
                d['email'].append(o)
            elif p == Namespaces.SITUACAO.value:
                d['situacao'].append(o)
            elif p == Namespaces.UNIDADE.value:
                d['departamento'].append(o)
    return d


def pega_artigos_livros_capitulos_teses(dados):
    """
    A partir do resultado da query QUERY_STRING,
        pega os artigos, livros, capitulos e teses do individuo
    :param dados: Binding sets da pesquisa do allegro
    :return dicionario com os itens "artigos", "livros", "capitulos" e "teses"
    """
    d: dict[str] = {'artigos': {}, 'livros': {}, 'capitulos': {}, 'teses': {}}

    # binding_set = {'tipo', 'Title', 'data', 'author_citation_name' ou 'author2')
    with dados:
        for bs in dados:
            # o tipo sera comparado com os valores do enumerador Ontologias
            tipo = str(bs.getValue('tipo'))
            # a data eh formada pelos ultimos 4 digitos, transformados para int
            data = int(str(bs.getValue("data")).strip('"')[-4:])
            # o titulo so precisa retirar as aspas
            titulo = str(bs.getValue('Title')).strip('"')
            # autor precisa retirar as aspas, e caso tenha mais de um, pegar somente o primeiro
            autor = str(bs.getValue('author2')).strip('"').split(';')[0]

            # sera salvo um dicionario {title, data: [autor]}
            id_dict = "[%d] %s" % (data, titulo)
            # esse dicionario sera inserido em algum dos seguintes
            if tipo == Namespaces.ARTIGO.value:
                dicionario_a_ser_inserido = d['artigos']
            elif tipo == Namespaces.LIVRO.value:
                dicionario_a_ser_inserido = d['livros']
            elif tipo == Namespaces.CAPITULO.value:
                dicionario_a_ser_inserido = d['capitulos']
            elif tipo == Namespaces.TESE.value:
                dicionario_a_ser_inserido = d['teses']
            else:
                continue
            # inserindo:
            if id_dict not in dicionario_a_ser_inserido:
                dicionario_a_ser_inserido[id_dict] = [autor]
            else:
                dicionario_a_ser_inserido[id_dict].append(autor)

    return d


def pega_documentos(dados):
    """
    A partir do resultado da query QUERY_STRING_LATTES,
        pega os documentos do professor
    :param dados: Binding sets da pesquisa do allegro
    :return dicionario com um item, documentos
    """
    d = {'documentos': {}}

    with dados:
        for bs in dados:
            # para a data, eh o mesmo esquema da funcao acima
            data = int(str(bs.getValue("data")).strip('"')[-4:])
            # para titulo, tambem
            titulo = str(bs.getValue("Title")).strip('"')
            # para o autor, utiliza-se a chave author_citation_name
            autor = str(bs.getValue("author_citation_name")).strip('"').split(";")[0]

            id_dict = "[%d] %s" % (data, titulo)
            if id_dict not in d['documentos']:
                d['documentos'][id_dict] = [autor]
            else:
                d['documentos'][id_dict].append(autor)

    return d


def pega_disciplinas(dados):
    """
    A partir do resultado da query QUERY_DISCIPLINAS,
        pega as disciplinas do professor
    :param dados: binding set da pesquisa do allegro
    :return: lista com dicionarios das disciplinas
    """
    lista = []
    with dados:
        for disciplina in dados:
            try:
                d = dict()
                d['nome'] = str(disciplina.getValue("course_name")).strip('"')
                d['codigo'] = str(disciplina.getValue("course_code")).strip('"')
                d['nomeDepartamento'] = str(disciplina.getValue("department_name")).strip('"')
                d['codDepartamento'] = str(disciplina.getValue("department_code")).strip('"')
                lista.append(d)
            except Exception as e:
                print("Algum erro ocorreu tentando ler uma disciplina: ", e)
    return lista


def pega_datas(dados):
    """
    A partir do resultado da query QUERY_QUANTIDADE,
        pega os ultimos 3 anos para pegar o veja mais do professor
    :param dados: binding set da pesquisa do allegro
    :return: lista com os anos possiveis
    """
    with dados:
        lista = [str(x.getValue("data")).strip('"') for x in dados]
    return lista


def pesquisa_about(pessoa: str, busca: str, codigo: Union[None, int] = None) -> Union[dict, str]:
    """
    Faz as queries para a página do about.
    :param pessoa: Nome do professor/orientador
    :param busca: string da pesquisa realizada
    :param codigo: codigo da pesquisa no banco, para ir atualizando enquanto a pesquisa eh realizada
    :return: Dicionario contendo as informações à serem exibidas na página da seguinte forma:

        "id_lattes": str -> numero do lattes
        "biografia": [str] -> biografias do professor. Se tiver uma em portugues, só haverá ela
        "homepage": [str] -> homepages do professor
        "email": [str] -> emails cadastrados do professor
        "situacao": str -> situacao do professor na PUC
        "departamento": str -> departamento do professor na PUC

    Caso algum erro ocorrá, será retornado uma string com o erro
    """
    # pesquisa os nomes
    # resultNomes = functions.getNomes(get_db(), busca)

    # inicia o contexto (para poder executar o sqlalchemy estando
    # fora do contexto do app (numa thread))
    if codigo is not None:
        ctx = create_app(getenv('FLASK_CONFIG')).app_context()
        ctx.push()
        carregamento = Carregamento.query.filter_by(id=codigo).first()
    else:
        carregamento = None
        ctx = None

    dicionario_final: dict[str] = {}  # NOVO

    try:
        repository = get_db()

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando lattes de %s" % pessoa, percent=5)
        print("Executando queryStringInfos")
        # query que retorna o lattes do professor
        queryStringInfos = QUERY_STRING_INFOS % pessoa
        # o que pode ser pego nessa query: foaf:member, bio:biography, foaf:citationName, foaf:name, foaf:homepage
        # nao retorna mbox

        infos = repository.executeTupleQuery(queryStringInfos)
        resultQueryStringInfos = pega_lattes_biografia_homepage(infos)
        if type(resultQueryStringInfos) == str:
            return resultQueryStringInfos  # a consulta deu erro, retorna o erro

        dicionario_final['id_lattes'] = resultQueryStringInfos['lattes']
        dicionario_final['homepage'] = resultQueryStringInfos['homepages']
        dicionario_final['biography'] = resultQueryStringInfos['biografias']

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando dados da PUC de %s" % pessoa, percent=15)
        print("Executando queryStringEmailHomepage")

        lattes = dicionario_final['id_lattes']
        id_nima = "http://www.nima.puc-rio.br/lattes/" + lattes + "#author-" + lattes
        queryStringEmailHomepage = QUERY_STRING_EMAIL_HOMEPAGE % id_nima
        emailhomepage = repository.executeTupleQuery(queryStringEmailHomepage)
        resultQueryEmailHomepage = pega_email_situacao_departamento(emailhomepage)

        dicionario_final['email'] = resultQueryEmailHomepage['email']
        dicionario_final['situacao'] = resultQueryEmailHomepage['situacao']
        dicionario_final['departamento'] = resultQueryEmailHomepage['departamento']
        # atualizando a lista de homepages
        for hp in resultQueryEmailHomepage['homepages']:
            if hp not in dicionario_final['homepage']:
                dicionario_final['homepage'].append(hp)

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando documentos de %s" % pessoa, percent=20)
        print("Executando queryString (query principal)")
        queryString = QUERY_STRING % (busca, pessoa, busca, pessoa)
        respostaQueryString = repository.executeTupleQuery(queryString)
        resultadoQueryString = pega_artigos_livros_capitulos_teses(respostaQueryString)

        dicionario_final['artigos'] = resultadoQueryString['artigos']
        dicionario_final['livros'] = resultadoQueryString['livros']
        dicionario_final['capitulos'] = resultadoQueryString['capitulos']
        dicionario_final['teses'] = resultadoQueryString['teses']

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando link lattes de %s" % pessoa, percent=45)
        print("Executando queryStringLattes (pesquisa de documentos)")
        # query para quando o usuário pesquisa pelo nome do professor
        queryStringLattes = QUERY_STRING_LATTES % (pessoa, pessoa)
        respostaQueryStringLattes = repository.executeTupleQuery(queryStringLattes)
        resultadoQueryStringLattes = pega_documentos(respostaQueryStringLattes)

        dicionario_final['documentos'] = resultadoQueryStringLattes['documentos']

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando disciplinas de %s" % pessoa, percent=60)
        print("Executando queryDisciplinas")
        queryDisciplinas = QUERY_DISCIPLINAS % (busca, pessoa)
        respostaQueryDisciplinas = repository.executeTupleQuery(queryDisciplinas)
        resultadoQueryDisciplinas = pega_disciplinas(respostaQueryDisciplinas)

        dicionario_final['lista_disciplinas'] = resultadoQueryDisciplinas

        # -------------------------------------------
        print("Ordenando os artigos/livros/capitulos/teses")
        # ordem cronológica inversa das produções (mais nova em primeiro na lista)
        # a ordenacao sera na chave de cada dicionario, sendo que o mais recente
        # para ordenar

        for key in ['artigos', 'livros', 'capitulos', 'teses']:
            d = dicionario_final[key]
            # sera gerado um novo dicionario, sendo que cada chave-conteudo sera adicionado na ordem correta
            # pois a partir do python 3.7, o dicionario mantem a ordem de inserção
            novo_d = dict()
            # pegando as chaves, ordenando pelo segundo elemento da chave (o ano), e comencando do maior
            for chave in sorted(d.keys(), key=lambda k: k[1], reverse=True):
                novo_d[chave] = d[chave]
            dicionario_final[key] = novo_d

        # -------------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando outros documentos de %s" % pessoa, percent=70)
        print("Executando queryQuantidade")
        # ultimos 3 anos em que producoes foram feitas para ser usado na query veja mais
        queryQuantidade = QUERY_QUANTIDADE % pessoa
        respostaQueryQuantidade = repository.executeTupleQuery(queryQuantidade)
        datas = pega_datas(respostaQueryQuantidade)
        if datas:
            print("Há datas para vejaMais, executando vejaMais")

            data_string = "' || ?data = '".join(datas[:3])
            queryVejaMais = QUERY_DINAMICA_VEJA_MAIS % (pessoa, data_string, pessoa, data_string)
            respostaQueryVejaMais = repository.executeTupleQuery(queryVejaMais)
            resultadoQueryVejaMais = pega_artigos_livros_capitulos_teses(respostaQueryVejaMais)

            dicionario_final['maisartigos'] = dict(
                itertools.islice(resultadoQueryVejaMais['artigos'].items(),
                                 quantidade_de_producoes_mostradas()))
            dicionario_final['maislivros'] = dict(
                itertools.islice(resultadoQueryVejaMais['livros'].items(),
                                 quantidade_de_producoes_mostradas()))
            dicionario_final['maiscapitulos'] = dict(
                itertools.islice(resultadoQueryVejaMais['capitulos'].items(),
                                 quantidade_de_producoes_mostradas()))
            dicionario_final['maisteses'] = dict(
                itertools.islice(resultadoQueryVejaMais['teses'].items(),
                                 quantidade_de_producoes_mostradas()))

        # -----------------------------------------
        if carregamento is not None:
            atualiza_status(carregamento, "Coletando outras disciplinas de %s" % pessoa, percent=90)
        print("Executando queryVejaMaisDisciplinas")
        queryVejaMaisDisciplinas = QUERY_VEJA_MAIS_DISCIPLINAS % pessoa
        respostaQueryVejaMaisDisciplinas = repository.executeTupleQuery(queryVejaMaisDisciplinas)
        resultadoQueryVejaMaisDisciplinas = pega_disciplinas(respostaQueryVejaMaisDisciplinas)

        dicionario_final['lista_vejamaisdisciplinas'] = resultadoQueryVejaMaisDisciplinas

        # -----------------------------------------
        print("Finalizado thread com codigo -->", codigo)
        if carregamento is not None:
            atualiza_status(carregamento, "Consulta de %s finalizada" % pessoa, percent=100)
            # salvando no arquivo
            filename = path.join(path.dirname(__file__), '..', 'pesquisas', f'{codigo}.json')
            print("Salvando o arquivo")
            with open(filename, 'w+') as f:
                dump(dicionario_final, f, indent=3)
            ctx.pop()
        return dicionario_final

    except Exception as e:
        print(e)
        return str(e)


# query para retornar o lattes do professor
QUERY_STRING_INFOS = """
    SELECT ?id ?p ?o
	WHERE
	{ 	
		?s dc:title ?title; bibo:identifier ?id; dc:creator ?author. ?author ?p ?o. 
		filter (regex(fn:lower-case(str(?title)), fn:lower-case('CV Lattes de'))) . 
		filter (regex(fn:lower-case(str(?title)), fn:lower-case('%s'))) . 
	}
"""

# query para pegar o email e homepage do reposiotorio matriculas_puc_etl
QUERY_STRING_EMAIL_HOMEPAGE = """
    PREFIX cad-puc: <http://www.nima.puc-rio.br/cad-puc/>
	SELECT distinct ?nome_professor_disciplina ?p ?o
	WHERE
	{
		?m ?p ?o ; foaf:name ?nome_professor_disciplina; (owl:sameAs|^owl:sameAs)* ?author_id.
		filter (?author_id = <%s>) .
		filter (?p in (foaf:homepage, foaf:mbox, cad-puc:situacao, cad-puc:unidade)).
	}
"""

# query geral para pegar as informações do autor
QUERY_STRING = """
    SELECT DISTINCT ?tipo ?Title ?data ?author2
	{
		{
			select (?prod_type AS ?tipo) (str(?title) as ?Title) ?data ?author2
			where
			{
				?s dc:title ?title; dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type; dcterms:issued ?data; dc:creator ?author2_id.
				?CVLattes dc:creator ?author.
				?author foaf:name ?author_name.
				(?s ?title) fti:match '%s' .
				?author2_id foaf:name ?author2 .
				filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) .
				filter (?prod_type IN
					(<http://purl.org/ontology/bibo/Thesis>,
					<http://purl.org/ontology/bibo/Article>,
					<http://purl.org/ontology/bibo/Book>,
					<http://purl.org/ontology/bibo/Chapter>) ).
				filter (strlen(str(?data)) < 5) .
			}
		}
		UNION
		{
			select (?prod_type AS ?tipo) (str(?title) as ?Title) ?data ?author2
			where
			{
				?s dc:title ?title; dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type; dcterms:issued ?data; dc:contributor ?author2_id.
				?CVLattes dc:creator ?author.
				?author foaf:name ?author_name.
				(?s ?title) fti:match '%s' .
				?author2_id foaf:name ?author2 .
				filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) .
				filter (?prod_type IN
					(<http://purl.org/ontology/bibo/Thesis>,
					<http://purl.org/ontology/bibo/Article>,
					<http://purl.org/ontology/bibo/Book>,
					<http://purl.org/ontology/bibo/Chapter>) ).
				filter (strlen(str(?data)) < 5) .
			}
		}
	}
	ORDER BY ?tipo ?Title ?author2
"""

# query para quando o usuário pesquisa pelo nome do professor
QUERY_STRING_LATTES = """
    SELECT DISTINCT (?prod_type AS ?tipo) (str(?title) as ?Title) ?data ?author_citation_name 
    WHERE 
    { 
        ?s dc:title ?title; rdf:type ?prod_type; dcterms:issued ?data; dc:creator ?author. 
        ?author foaf:name ?author_name. 
        ?author foaf:citationName ?author_citation_name . 
        (?s ?title) fti:match '%s' . 
        filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) . 
        filter (?prod_type IN (<http://xmlns.com/foaf/0.1/Document>) ). 
    }
"""

# query para as informacoes das disciplinas
QUERY_DISCIPLINAS = """
    SELECT ?course_name ?course_code ?department_name ?department_code
    WHERE                     
    {
        ?C ccso:csName ?course_name; ccso:code ?course_code; ccso:hasSyllabus ?S.
        ?S ccso:hasInstructor ?I.
        ?I foaf:name ?instructor_name.
        ?D ccso:offersCourse ?C; sch:legal_name ?department_name; sch:identifier ?department_code.
        (?C ?course_name) fti:match '%s'.
        filter (regex(fn:lower-case(str(?instructor_name)), fn:lower-case('%s')))
    }
"""

# query para veja mais
QUERY_QUANTIDADE = """
    SELECT distinct ?data
    WHERE
    {
        ?s dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type; dcterms:issued ?data.
        ?CVLattes dc:creator ?author.
        ?author foaf:name ?author_name.
        filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) . 
        filter (?prod_type IN (<http://purl.org/ontology/bibo/Article>,
                            <http://purl.org/ontology/bibo/Thesis>,
                            <http://purl.org/ontology/bibo/Book>, 
                            <http://purl.org/ontology/bibo/Chapter>)).
        filter (strlen(str(?data)) < 5) .
    }
    ORDER BY DESC (?data)
    LIMIT 3
"""

# query para disciplinas do veja mais
QUERY_VEJA_MAIS_DISCIPLINAS = """
    SELECT ?course_name ?course_code ?department_name ?department_code
    WHERE                     
    {
        ?C ccso:csName ?course_name; ccso:code ?course_code; ccso:hasSyllabus ?S.
        ?S ccso:hasInstructor ?I.
        ?I foaf:name ?instructor_name.
        ?D ccso:offersCourse ?C; sch:legal_name ?department_name; sch:identifier ?department_code.
        filter (regex(fn:lower-case(str(?instructor_name)), fn:lower-case('%s')))
    }
"""

QUERY_DINAMICA_VEJA_MAIS = """
    select distinct ?tipo ?Title ?data ?author2
    {
        {
            select (?prod_type AS ?tipo) (str(?title) as ?Title) ?data ?author2
            where
            {
                ?s dc:title ?title; dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type; dcterms:issued ?data; dc:creator ?author2_id . 
                ?CVLattes dc:creator ?author. 
                ?author foaf:name ?author_name. 
                ?author2_id foaf:name ?author2 .   
                filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) .  
                filter (?prod_type IN (
                    <http://purl.org/ontology/bibo/Thesis>, 
                    <http://purl.org/ontology/bibo/Article>, 
                    <http://purl.org/ontology/bibo/Book>, 
                    <http://purl.org/ontology/bibo/Chapter>
                )).
                filter (strlen(str(?data)) < 5) .
                filter (?data = '%s').
            }
        }
        UNION
        {
            select (?prod_type AS ?tipo) (str(?title) as ?Title) ?data ?author2 
            where
            {
                ?s dc:title ?title; dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type; dcterms:issued ?data; dc:contributor ?author2_id . 
                ?CVLattes dc:creator ?author. 
                ?author foaf:name ?author_name.
                ?author2_id foaf:name ?author2 .
                filter (regex(fn:lower-case(str(?author_name)), fn:lower-case('%s'))) .  
                filter (?prod_type IN (
                    <http://purl.org/ontology/bibo/Thesis>, 
                    <http://purl.org/ontology/bibo/Article>, 
                    <http://purl.org/ontology/bibo/Book>, 
                    <http://purl.org/ontology/bibo/Chapter>
                )).
                filter (strlen(str(?data)) < 5) .
                filter (?data = '%s').
            }
        }
    }
    ORDER BY DESC(?data)
"""
