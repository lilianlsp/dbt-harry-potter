# Infraestrutura: S3 + Snowflake (Storage Integration)

Este documento descreve o setup de infraestrutura feito antes de qualquer transformação em dbt: como os dados brutos chegam até o Snowflake.

## Por que S3 + Storage Integration (em vez de upload direto)

Duas formas de acessar S3 a partir do Snowflake:

| Abordagem | Como funciona | Segurança |
|---|---|---|
| Credenciais diretas | Access Key + Secret Key coladas no `CREATE STAGE` | Chave fixa, risco se vazar |
| Storage Integration | Snowflake assume uma IAM Role via `AssumeRole`, sem chave secreta | Padrão de produção |

Optamos por Storage Integration para praticar o padrão usado em ambientes reais.

## 1. Bucket S3

Bucket dedicado a este projeto, separado de outros projetos de portfólio (isolamento de permissões).

Configurações:
- **Bucket type**: General purpose
- **Object Ownership**: ACLs disabled / Bucket owner enforced
- **Block Public Access**: todos os checkboxes marcados
- **Versioning**: Disabled
- **Encryption**: SSE-S3 (chave gerenciada pela AWS, sem configuração extra)

Estrutura de pastas:
```
<bucket>/
  raw/
    box_office/
    characters/
    houses/
    movies/
```

## 2. IAM Policy (menor privilégio)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SnowflakeS3ListBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket-name>",
      "Condition": {
        "StringLike": { "s3:prefix": ["raw/*"] }
      }
    },
    {
      "Sid": "SnowflakeS3ReadWrite",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::<bucket-name>/raw/*"
    }
  ]
}
```

Sem `s3:DeleteObject`: não é necessário para `COPY INTO` (que só lê com `GetObject`), e mantém a policy mais restrita.

## 3. IAM Role

Role dedicada, assumida pelo Snowflake via `sts:AssumeRole`. O setup segue uma dependência circular conhecida:

1. Role criada com trust relationship temporário (placeholder)
2. Storage Integration criada no Snowflake, referenciando o ARN da Role
3. Snowflake retorna `STORAGE_AWS_IAM_USER_ARN` e `STORAGE_AWS_EXTERNAL_ID`
4. Trust relationship da Role atualizado com os valores reais

## 4. Storage Integration

```sql
CREATE STORAGE INTEGRATION <integration_name>
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<account-id>:role/<role-name>'
    STORAGE_ALLOWED_LOCATIONS = ('s3://<bucket-name>/raw/');

DESC STORAGE INTEGRATION <integration_name>;
```

## 5. Trust Relationship final (AWS)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "<STORAGE_AWS_IAM_USER_ARN>" },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": { "sts:ExternalId": "<STORAGE_AWS_EXTERNAL_ID>" }
      }
    }
  ]
}
```

## 6. Database, schema e warehouse (Snowflake)

```sql
CREATE DATABASE IF NOT EXISTS hp_project;
CREATE SCHEMA IF NOT EXISTS hp_project.raw;
GRANT OPERATE ON WAREHOUSE COMPUTE_WH TO ROLE TRANSFORM;
```

Warehouse compartilhado com outros projetos: compute não tem relação de propriedade com um projeto específico.

## 7. Stage

```sql
CREATE OR REPLACE STAGE hp_project.raw.s3_raw_stage
    STORAGE_INTEGRATION = <integration_name>
    URL = 's3://<bucket-name>/raw/'
    FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"');
```

> O `URL` precisa terminar em `/` quando aponta para uma pasta, consistente com `STORAGE_ALLOWED_LOCATIONS`.

## 8. Teste de conexão

```sql
LIST @hp_project.raw.s3_raw_stage;
```

Bucket vazio → resultado esperado é zero linhas, sem erro. Confirma que toda a cadeia (S3 → IAM Policy → IAM Role → Trust Relationship → Storage Integration → Stage) está funcionando.

## Erros encontrados durante o setup

| Erro | Causa | Correção |
|---|---|---|
| `STORAGE_ALLOWED_LOCATIONS` como string simples | Parâmetro espera uma lista | Envolver em parênteses |
| `URL` do stage sem barra final | Inconsistência com `STORAGE_ALLOWED_LOCATIONS` | Adicionar `/` no final |
| `AUTO_SUSPENDED` no `CREATE WAREHOUSE` | Nome de parâmetro errado | Corrigir para `AUTO_SUSPEND` |
| `Database does not exist or not authorized` | Comando não persistiu / contexto de role diferente | Rodar novamente |

## Nota de organização (atualização pós-carga)

Na prática, as 6 tabelas do dataset maricinnamon acabaram todas na mesma subpasta (`raw/movies/`) por decisão durante a execução, em vez de uma subpasta por tabela como planejado originalmente. Funcionalmente não afeta o `COPY INTO` (ele aponta pro arquivo exato), só a organização visual do bucket. Ver `docs/loading-tables.md` para o fluxo completo de carga e os erros encontrados nessa etapa (incluindo um problema de encoding não coberto neste documento original).

## Custo

- Storage S3: frações de centavo por GB/mês (CSVs pequenos, custo irrelevante)
- Warehouse Snowflake: cobrado só por tempo ativo (`AUTO_SUSPEND` configurado para desligar após 60s ocioso)
- Recomendado: configurar AWS Budgets (billing alert) e um Resource Monitor no Snowflake como redes de segurança
