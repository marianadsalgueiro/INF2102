#!/bin/bash

echo "Iniciando o script:"
cd lattes-alunos-xml/

echo "Convertendo os xmls em rdfs..."
for f in *.xml
do
    newFile=${f/${f: -4}/} 

    # need to install libxml2, libxslt
    xsltproc --stringparam ID $newFile ../lattes_alunos.xsl $f > $newFile".rdf"
done

echo "Movendo rdfs para diretorio separado ..."
mv *.rdf ../lattes-alunos-rdf/


