# Harry Potter Analytics — dbt + Snowflake

Projeto de portfólio construído para praticar Analytics Engineering de ponta a ponta: ingestão de dados brutos (API + CSV), infraestrutura de storage na nuvem, e transformação em camadas com dbt.

> Status: em construção. Este README é atualizado conforme o projeto avança.

## O que este projeto faz

Combina dados de personagens, casas e filmes de Harry Potter (HP-API / PotterDB) com dados de bilheteria dos filmes (Kaggle), modelados em camadas staging → intermediate → marts usando dbt, rodando sobre Snowflake.

## Arquitetura

```
HP-API / PotterDB ──┐
                     ├──► S3 (raw) ──► Snowflake (RAW schema) ──► dbt (staging → intermediate → marts)
Kaggle CSV ──────────┘
```

Detalhes completos da infraestrutura (bucket S3, IAM, Storage Integration) em [`docs/infra-setup.md`](docs/infra-setup.md).

## Decisões técnicas e por quê

- **S3 como camada de ingestão, não upload direto no Snowflake**: simula um pipeline de dados real, onde o dado pousa num data lake antes de ser transformado.
- **Storage Integration em vez de Access Key**: identidade temporária via IAM Role (`AssumeRole`), sem chave secreta exposta em nenhum lugar. Padrão usado em ambientes de produção.
- **IAM Role e Storage Integration dedicadas a este projeto**: isolamento de permissões (princípio do menor privilégio) em vez de reaproveitar credenciais de outros projetos de portfólio.
- **Warehouse compartilhado (`COMPUTE_WH`)**: warehouse é poder de computação, não armazenamento — não há necessidade de isolar por projeto.

## Estrutura do repositório

```
harry-potter-dbt/
├── docs/
│   └── infra-setup.md       # setup de AWS S3 + Snowflake, passo a passo
├── models/
│   ├── staging/              # limpeza e padronização das fontes brutas
│   ├── intermediate/         # joins e transformações intermediárias
│   └── marts/                # modelos finais de consumo
├── seeds/                    # dados fixos (casas de Hogwarts)
├── tests/                    # testes customizados
├── dbt_project.yml
└── packages.yml
```

## Como rodar

*(seção a preencher conforme o projeto avança: setup do profiles.yml, comandos dbt run/test/docs)*

## Stack

dbt · Snowflake · AWS S3 · IAM · Python (extração via API)
