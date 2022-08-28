#!/bin/bash

cd ~/Downloads/professores2

echo "Iniciando o script:"

echo "Convertendo os xmls em rdfs..."
for f in *.xml
do
    newFile=${f/${f: -4}/} 

    # need to install libxml2, libxslt
    xsltproc ../lattes.xsl $f > $newFile".rdf"
done



