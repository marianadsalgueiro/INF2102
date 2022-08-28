#!/bin/bash

echo "Iniciando o script:"
cd lattes-professores-xml/

echo "Convertendo os xmls em rdfs..."
for f in *.xml
do
    newFile=${f/${f: -4}/} 

    # need to install libxml2, libxslt
    xsltproc --stringparam ID $newFile ../lattes_professores.xsl $f > $newFile".rdf"
done

echo "Movendo rdfs para diretorio separado ..."
find . -name "*.rdf" -type f | head -546 | while read arq; do mv "$arq" ../lattes-professores-rdf/; done;
mv *.rdf ../lattes-professores2-rdf/


