# Instalação do AllegroGraph 7.0.3

Autora: Mariana Salgueiro

A documentação a seguir se refere a instalação do AllegroGraph 7.0.3 no ambiente Ubuntu 18.04.6 LTS.

## Instalação no ambiente

```
curl -O https://franz.com/ftp/pri/acl/ag/ag7.0.3/linuxamd64.64/agraph-7.0.3-linuxamd64.64.tar.gz
tar zxf agraph-7.0.3-linuxamd64.64.tar.gz 
```

Esse passo cria o diretório "agraph-7.0.3".

```
agraph-7.0.3/install-agraph <caminho>/ag-7.0.3
```

## Subindo o banco de dados
Você pode iniciar o AllegroGraph executando:
```
/home/joe/tmp/ag7.3.0/bin/agraph-control --config <caminho>/ag7.3.0/lib/agraph.cfg start  
```

Você pode parar o AllegroGraph executando:  
```
/home/joe/tmp/ag7.3.0/bin/agraph-control --config <caminho>/ag7.3.0/lib/agraph.cfg stop
```

## Verificando se o AllegroGraph está executando:
Abra um navegador e entre na URL do AllegroGraph WebView:
http://localhost:10035