DROP TABLE IF EXISTS usuario CASCADE;

CREATE TABLE usuario
(
	pk_email varchar(60),
    nome varchar(120) NOT NULL,
	senha varchar(128) NOT NULL,
	
	CONSTRAINT usuario_pk PRIMARY KEY (pk_email)
);

DROP TABLE IF EXISTS busca CASCADE;

CREATE TABLE busca
(
    pk_id serial, 
	data_e_hora TIMESTAMP NOT NULL,
    palavra_buscada varchar(50) NOT NULL,
    ip varchar(20),
    sistema_operacional varchar(20),
    browser varchar(20), 
    professor_selecionado varchar(100),
	
	CONSTRAINT busca_pk PRIMARY KEY (pk_id)
);

DROP TABLE IF EXISTS frequencia_termos CASCADE;

CREATE TABLE frequencia_termos
(
    pk_palavra varchar(50),
    count integer NOT NULL,
	
	CONSTRAINT frequencia_termos_pk PRIMARY KEY (pk_palavra)
);