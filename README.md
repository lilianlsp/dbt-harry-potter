# Harry Potter Analytics — dbt + Snowflake

Projeto de portfólio construído para praticar Analytics Engineering de ponta a ponta: ingestão de dados brutos de múltiplas fontes (Kaggle + API), infraestrutura de storage na nuvem, e transformação em camadas com dbt.

> Status: em construção. Este README é atualizado conforme o projeto avança.

## O que este projeto faz

Duas frentes de análise sobre o universo de Harry Potter:

1. **Mundo mágico**: personagens, casas, filmes, feitiços e lugares, modelados com dados vindos de três fontes diferentes (dois datasets do Kaggle + a HP-API), carregados de propósito com sobreposição para praticar reconciliação de dados na camada intermediate.
2. **Fluência em inglês**: quanto do vocabulário falado nos livros/filmes de Harry Potter é coberto por listas de palavras comuns do inglês (General Service List), em diferentes registros — geral, geral falado e de negócios.

## Arquitetura

```
Kaggle (maricinnamon: characters, movies, places, spells,   ─┐
        chapters, dialogue)                                  │
Kaggle (kornflex: transcrição completa)                       ├──► S3 (raw) ──► Snowflake (RAW) ──► dbt
Kaggle (books: vendas, palavras, data de publicação)          │      (staging → intermediate → marts)
HP-API / PotterDB (characters, houses, movies)                │
GSL (seeds: business / general / general_spoken)             ─┘
```

Detalhes completos da infraestrutura (bucket S3, IAM, Storage Integration) em [`docs/infra-setup.md`](docs/infra-setup.md), das fontes de dados em [`docs/sources.md`](docs/sources.md), e do fluxo de carga em [`docs/loading-tables.md`](docs/loading-tables.md).

## Decisões técnicas e por quê

- **S3 como camada de ingestão, não upload direto no Snowflake**: simula um pipeline de dados real, onde o dado pousa num data lake antes de ser transformado.
- **Storage Integration em vez de Access Key**: identidade temporária via IAM Role (`AssumeRole`), sem chave secreta exposta. Padrão de produção.
- **Fontes sobrepostas de propósito**: characters e movies aparecem em três fontes diferentes (maricinnamon, kornflex/dialogue, HP-API). Em vez de evitar a duplicidade, o projeto a mantém para praticar reconciliação de dados real — uma habilidade central de Analytics Engineering.
- **Camada raw sempre como texto (`VARCHAR`)**: nenhuma conversão de tipo na carga, para que o `COPY INTO` nunca quebre por formatação inesperada. Conversão e limpeza acontecem só na staging.
- **Warehouse compartilhado (`COMPUTE_WH`)**: warehouse é poder de computação, não armazenamento — não há necessidade de isolar por projeto.

## Estrutura do repositório

```
harry-potter-dbt/
├── docs/
│   ├── infra-setup.md        # setup de AWS S3 + Snowflake, passo a passo
│   ├── sources.md            # cada fonte de dado, papel no projeto e status
│   └── loading-tables.md     # fluxo de carga replicável + erros encontrados
├── models/
│   ├── staging/               # limpeza e padronização das fontes brutas
│   ├── intermediate/          # joins, reconciliação entre fontes, transformações
│   └── marts/                 # modelos finais de consumo
├── seeds/
│   ├── gsl_business.csv
│   ├── gsl_general.csv
│   └── gsl_general_spoken.csv
├── tests/                     # testes customizados
├── dbt_project.yml
└── packages.yml
```

## Como rodar

*(seção a preencher conforme o projeto avança: setup do profiles.yml, comandos dbt run/test/docs)*

## Stack

dbt · Snowflake · AWS S3 · IAM · Python (extração via API)
