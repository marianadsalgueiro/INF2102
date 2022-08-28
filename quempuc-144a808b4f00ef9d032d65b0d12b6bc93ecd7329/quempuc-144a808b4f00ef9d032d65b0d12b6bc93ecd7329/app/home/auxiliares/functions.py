# ---------------------------------------------------------------------------
# Author: Mariana Salgueiro
# ---------------------------------------------------------------------------

from flask import render_template
import logging
import traceback 
import threading

from . import atualiza_status
from ...models import Carregamento


# Inicialização da variável que guarda o logger do módulo
logger = logging.getLogger(__name__)


def searchInRepository(repository, string_buscada, atualizar_status=None):

    if atualizar_status is not None:
        percentual_atual = atualizar_status.percent
        percentual_faltando = 100 - percentual_atual
        percentual_por_thread = percentual_faltando // 7

    else:
        percentual_atual = None
        percentual_por_thread = None

    resultsArtigos = {}
    resultsLivros = {}
    resultsCapitulos = {}
    resultsTeses = {}
    resultsDisciplinas = {}
    resultsBios = {}
    resultsLattes = {}

    try:
        artigos = threading.Thread(target=getStringBuscada, args=(repository, string_buscada, resultsArtigos, 'Article'))
        livros = threading.Thread(target=getStringBuscada, args=(repository, string_buscada, resultsLivros, 'Book'))
        capitulos = threading.Thread(target=getStringBuscada, args=(repository, string_buscada, resultsCapitulos, 'Chapter'))
        teses = threading.Thread(target=getStringBuscada, args=(repository, string_buscada, resultsTeses, 'Thesis'))
        disciplinas = threading.Thread(target=getDisciplinas, args=(repository, string_buscada, resultsDisciplinas))
        bios = threading.Thread(target=getBio, args=(repository, string_buscada, resultsBios))
        lattes = threading.Thread(target=getLattes, args=(repository, string_buscada, resultsLattes))

        threads = [artigos, livros, capitulos, teses, disciplinas, bios, lattes]

        for t in threads:
            t.start()

        for i, t in enumerate(threads):
            t.join()
            # atualiza o status se tiver
            if atualizar_status is not None:
                atualiza_status(atualizar_status, "Coletando dados gerais",
                                percentual_atual + percentual_por_thread * i)

    except Exception as e:
        print(traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s', print(traceback.format_exc()))
        return render_template("errors/error.html")

    return resultsArtigos, resultsLivros, resultsCapitulos, resultsTeses, resultsDisciplinas, resultsBios, resultsLattes


def getStringBuscada(repository, string_buscada, dic, tipo):
#query da página principal que retorna professores em abas artigos/livros/teses/capitulos
    queryString = """ 
        PREFIX cad-puc: <http://www.nima.puc-rio.br/cad-puc/>
        SELECT DISTINCT ?author_name (COUNT(?%s) as ?count%s)
        {
            SELECT DISTINCT ?author_name (str(?title) as ?%s)
            WHERE
            {
                ?s dc:title ?title; dcterms:isReferencedBy ?CVLattes; rdf:type ?prod_type.
                ?CVLattes dc:creator ?author.
                ?author foaf:name ?author_name; foaf:member ?UnivOrigem.
                ?m (owl:sameAs|^owl:sameAs)* ?author; cad-puc:situacao ?situacao_professor.
                (?s ?title) fti:match '%s' .
                filter (?UnivOrigem = <http://www.nima.puc-rio.br/lattes/PUC-RIO>).
                filter (?prod_type IN (<http://purl.org/ontology/bibo/%s>) ) .
                filter (?situacao_professor in ('ATIVO', 'LICENCIADO'))
            }
        }
        group by ?author_name
        """ % (tipo,tipo,tipo,string_buscada, tipo)

    try:
        result = repository.executeTupleQuery(queryString)

        var = 'count%s' % tipo #criando variável do tipo countArticle/countBook para ir de acordo com o que já estava feito no HTML

        for binding_set in result:
            authorName = str(binding_set.getValue("author_name"))
            authorName=authorName[1:-1] # fora os " "
            count = int(str(binding_set.getValue(var)).replace('"^^<http://www.w3.org/2001/XMLSchema#integer>',"").strip('"')) 
        
            dic.update({authorName : {
                var: count,
            }})

    except Exception as e:
        print(traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s', print(traceback.format_exc()))
        return render_template("errors/error.html")


def getDisciplinas(repository, busca, dic): #caso de Antonio Luz Furtado que nao consigo achar o idp
    queryString = """
        SELECT ?instructor_name (COUNT(?course_name) AS ?nOcorrencias)
        {	
            SELECT ?course_name ?instructor_name
            WHERE                     
            {
                ?C ccso:csName ?course_name; ccso:hasSyllabus ?S.
                ?S ccso:hasInstructor ?I.
                ?I foaf:name ?instructor_name.
                (?C ?course_name) fti:match '%s'.
            }
        }
        GROUP BY ?instructor_name
    """ % busca

    try:
        result = repository.executeTupleQuery(queryString)

        #{'instructor_name': '"AGNIESZKA EWA LATAWIEC"', 'nOcorrencias': '"1"^^<http://www.w3.org/2001/XMLSchema#integer>'}
        for binding_set in result:
            instructor_name = str(binding_set.getValue("instructor_name"))
            instructor_name=instructor_name[1:-1] # fora os " "
            count = int(str(binding_set.getValue("nOcorrencias")).replace('"^^<http://www.w3.org/2001/XMLSchema#integer>',"").strip('"')) 

            queryStringInfos = """
                SELECT DISTINCT ?id
                WHERE
                { 	
                    ?s dc:title ?title; bibo:identifier ?id . 
                    filter (regex(fn:lower-case(str(?title)), fn:lower-case('CV Lattes de'))) . 
                    filter (regex(fn:lower-case(str(?title)), fn:lower-case('%s'))) . 
                }  
            """ % (instructor_name)

            #nao sera mais necessario quando linkarmos profs das bases
            check = repository.executeTupleQuery(queryStringInfos)

            for binding_set in check:
                ident = str(binding_set.getValue("id"))
                
                #só insere no dicionario se encontrarmos o lattes do professor (já que por enquanto as bases não estão unificadas)
                if ident:
                    dic.update({instructor_name : {
                        'countDisciplinas': count,
                    }})

    except Exception as e:
        print(traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s', print(traceback.format_exc()))
        return render_template("errors/error.html")

def getBio(repository, busca, dic):
    queryString = """
        SELECT DISTINCT ?author_name (COUNT(?bio) as ?countBio)
        {
            SELECT DISTINCT ?author_name ?bio
            WHERE
            {
                ?s bio:biography ?bio; foaf:name ?author_name; foaf:member ?UnivOrigem.
                (?s ?bio) fti:match '%s' .
                filter (?UnivOrigem = <http://www.nima.puc-rio.br/lattes/PUC-RIO>).
                filter (lang(?bio) = 'pt') .
            }
        }
        group by ?author_name
    """ % (busca)

    try:
        result = repository.executeTupleQuery(queryString)

        for binding_set in result:
            print(binding_set)
            authorName = str(binding_set.getValue("author_name"))
            authorName=authorName[1:-1] # fora os " "
            countBio = int(str(binding_set.getValue("countBio")).replace('"^^<http://www.w3.org/2001/XMLSchema#integer>',"").strip('"'))

            dic.update({authorName : {
                'countBio': countBio,
            }})

    except Exception as e:
        print(traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s', print(traceback.format_exc()))
        return render_template("errors/error.html")


def getLattes(repository, busca, dic):
    queryString = """
        SELECT ?author_name (count(?author_name) as ?countCV)
        {
            SELECT DISTINCT ?author_name (str(?title) as ?Title)
            WHERE
            {
                ?CVLattes dc:title ?title; dc:creator ?author; rdf:type ?prod_type.
                ?author foaf:name ?author_name; foaf:member ?UnivOrigem.
                (?s ?author_name) fti:match '%s' .
                filter (?UnivOrigem = <http://www.nima.puc-rio.br/lattes/PUC-RIO>).
                filter (?prod_type = <http://xmlns.com/foaf/0.1/Document>) .
            }
        }
        group by ?author_name
    """ % (busca)

    try:
        result = repository.executeTupleQuery(queryString)

        for binding_set in result:
            print(binding_set)
            authorName = str(binding_set.getValue("author_name"))
            authorName=authorName[1:-1] # fora os " "
            countCV = int(str(binding_set.getValue("countCV")).replace('"^^<http://www.w3.org/2001/XMLSchema#integer>',"").strip('"')) if str(binding_set.getValue("countCV")) != 'None' else str(binding_set.getValue("countCV"))

            dic.update({authorName : {
                'countCV': countCV,
            }})

    except Exception as e:
        print(traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s' % traceback.format_exc())
        return render_template("errors/error.html")


def getNomes(repositorio, pesquisa: str):
    """
    Faz uma pesquisa no repositorio buscando todos os nomes
    que contenham o termo pesquisado no nome

    :param repositorio: Repositorio do Allegro
    :param pesquisa: termo pesquisado
    :return: lista com os nomes
    """

    # limpando a pesquisa, e colocando * no inicio e fim
    pesquisa_limpa = pesquisa.strip(' \t\n*?"')   # retira possiveis caracteres ruins

    query = """
        SELECT DISTINCT ?author_name (str(?title) as ?Title)
        WHERE
        {
            ?CVLattes dc:title ?title; dc:creator ?author; rdf:type ?prod_type.
            ?author foaf:name ?author_name; foaf:member ?UnivOrigem.
            (?s ?author_name) fti:match '%s' .
            filter (?UnivOrigem = <http://www.nima.puc-rio.br/lattes/PUC-RIO>).
            filter (?prod_type = <http://xmlns.com/foaf/0.1/Document>) .
        }
        """ % pesquisa_limpa

    # fazendo a pesquisa
    try:
        resultado = repositorio.executeTupleQuery(query=query)
        lista_nomes = [str(x.getValue("author_name")).strip('"') for x in resultado]  # pega somente os nomes
        print("LISTA DE PROFESSORES: ", lista_nomes)
        return lista_nomes

    except Exception as e:   # aborta
        print("#### ERRO COLETANDO PROFESSORES ####")
        print("ERRO -> ", e)
        print("TRACEBACK -> ", traceback.format_exc())
        logger.error('Aconteceu alguma excecao ao fazer a busca nos repositorios: %s' % traceback.format_exc())
        return render_template("errors/error.html")
