Colocar a pasta lattes_professores que o Tomás mandou na VM.
Rodar o script 'novoslattes.sh'.
Criar os repositórios no allegro.
Executar no terminal da VM dentro da nova pasta de lattes criada:
    ~/ag-7.0.3/bin/agtool load --port 10035 --input rdfxml <NOME_REPOSITORIO> lattes-professores-rdf/*.rdf
    ~/ag-7.0.3/bin/agtool load --port 10035 --input rdfxml <NOME_REPOSITORIO> lattes-professores2-rdf/*.rdf

Verificar a quantidade de triplas carregadas em cada repositório e o tempo de carga
A cada carga executada é importante registrar no Blog do NIMA com um post como esse: https://biobdnima.blogspot.com/2020/02/revisao-da-conversao-e-carga-do-lattes.html