#!/bin/bash

cd lattes_alunos-zip/

echo "Iniciando o script:"

echo "Extraindo os xmls de alunos dos arquivos .zip..."

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for f in *.zip
do
    unzip $f
done
