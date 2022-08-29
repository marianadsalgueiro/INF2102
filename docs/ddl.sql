DROP TABLE IF EXISTS busca CASCADE;

CREATE TABLE busca
(
    pk_id serial, 
	data_e_hora TIMESTAMP NOT NULL,
    palavra_buscada varchar(50) NOT NULL,
    ip varchar(20),
    sistema_operacional varchar(20),
    browser varchar(20), 
	
	CONSTRAINT busca_pk PRIMARY KEY (pk_id)
);

DROP TABLE IF EXISTS frequencia_termos CASCADE;

CREATE TABLE frequencia_termos
(
    pk_palavra varchar(50),
    count integer NOT NULL,
	
	CONSTRAINT frequencia_termos_pk PRIMARY KEY (pk_palavra)
);

DROP TABLE IF EXISTS carregamento CASCADE;

CREATE TABLE carregamento
(
    id serial,
    status varchar(100),
    percent integer,
    nome varchar(100),
    busca varchar(100),
    flagNome integer,

    CONSTRAINT carregamento_pk PRIMARY KEY (id)
)