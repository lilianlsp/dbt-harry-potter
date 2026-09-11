# Fluxo de carga (S3 → Snowflake)

Passo a passo replicável usado para cada tabela bruta do projeto.

## Fluxo geral

1. Ver a estrutura real do arquivo (`head -5 arquivo.csv`)
2. Desenhar o `CREATE TABLE` no schema `raw`, tudo como `VARCHAR`, sem limite de tamanho
3. Subir o arquivo pro S3, na subpasta dentro de `raw/`
4. Confirmar visibilidade no Snowflake (`LIST @stage/subpasta/;`)
5. Rodar o `COPY INTO`
6. Validar com `SELECT *`

## Por que a raw é sempre `VARCHAR`

Se o tipo certo (`INTEGER`, `DATE`) fosse forçado já na carga, qualquer linha com formato inesperado faria o `COPY INTO` falhar ou truncar dado. Guardando tudo como texto, a carga nunca quebra por formatação — conversão e limpeza acontecem na staging.

## Encoding (`Invalid UTF8 detected`)

Datasets exportados de Excel/Windows costumam vir em Windows-1252/ISO-8859-1, não UTF-8. Resolvido com `ENCODING = 'ISO-8859-1'` no `FILE_FORMAT` do `COPY INTO`:

```sql
COPY INTO hp_project.raw.characters
FROM @hp_project.raw.s3_raw_stage/movies/Characters.csv
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' ENCODING = 'ISO-8859-1');
```

## Erros encontrados

| Erro | Causa | Correção |
|---|---|---|
| `LIST @stage.subpasta` → objeto inexistente | Ponto em vez de barra separando subpasta | `@stage/subpasta/` |
| `LIST` vazio com arquivo já subido | Comando rodado antes do upload terminar | Repetir o `LIST` |
| `COPY INTO` com `;` no meio | Ponto e vírgula fechando antes do `FILE_FORMAT` | Um `;` só, no final |
| `FILE_FORMAT(...)` sem `=` | Sintaxe incompleta | `FILE_FORMAT = (...)` |
| `Invalid UTF8 detected` | Encoding do arquivo não é UTF-8 | `ENCODING = 'ISO-8859-1'` |
| `CREATE OR REPLACE hp_project.raw.movies(...)` | Faltou `TABLE` | `CREATE OR REPLACE TABLE ...` |
| `CREATE TABLE places\n place_id VARCHAR,` | Faltou `(` de abertura | `CREATE TABLE places (` |

## Nota de organização

As 6 tabelas do maricinnamon foram carregadas na mesma subpasta `raw/movies/` do S3 (decisão prática durante a execução), em vez de uma subpasta por tabela. O `COPY INTO` não é afetado (aponta pro arquivo exato), mas o nome da pasta não reflete o conteúdo real.
