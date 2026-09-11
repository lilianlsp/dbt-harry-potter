# Fontes de dados

## Mundo mágico

### 1. [maricinnamon — Harry Potter Movies Dataset](https://www.kaggle.com/datasets/maricinnamon/harry-potter-movies-dataset) ✅
7 tabelas relacionadas com IDs prontos pra join: `Chapters`, `Characters`, `Data_Dictionary`, `Dialogue`, `Movies`, `Places`, `Spells`. Fonte principal do domínio "mundo mágico" + uma das duas fontes de diálogo.

**Achado**: `Movies.csv` já traz `Box Office` nativo — cobre bilheteria sem precisar de dataset separado.

Carregado em `hp_project.raw`: `characters`, `chapters`, `dialogue`, `movies`, `places`, `spells`. Exigiu `ENCODING = 'ISO-8859-1'` no `COPY INTO`.

### 2. [kornflex — Harry Potter Movies Dataset (Scripts/Transcripts)](https://www.kaggle.com/datasets/kornflex/harry-potter-movies-dataset) ⬜
Transcrição completa da saga. Segunda fonte de diálogo, carregada de propósito ao lado do `Dialogue` do maricinnamon, para reconciliar as duas na camada intermediate.

### 3. HP-API / PotterDB ⬜
Endpoints REST de characters, houses e movies. Terceira fonte de characters/movies, carregada via script Python, para reconciliar com as duas fontes do Kaggle.

## Livros

### 4. [adnananam — Harry Potter Dataset (Books)](https://www.kaggle.com/datasets/adnananam/harry-potter-dataset) ✅
Cópias vendidas, palavras faladas, data de publicação — uma linha por livro. Carregado em `hp_project.raw.books`.

## Referência de vocabulário

### 5. GSL — General Service List ⬜
Três seeds separados (`gsl_business.csv`, `gsl_general.csv`, `gsl_general_spoken.csv`), usados para calcular cobertura de vocabulário comum do inglês no diálogo dos livros/filmes.

## Datasets descartados

- [gulsahdemiryurek/harry-potter-dataset](https://www.kaggle.com/datasets/gulsahdemiryurek/harry-potter-dataset) — script só dos 3 primeiros filmes
- [zez000/characters-in-harry-potter-books](https://www.kaggle.com/datasets/zez000/characters-in-harry-potter-books) — redundante com as fontes escolhidas
- [aditya126/movies-box-office-dataset-2000-2024](https://www.kaggle.com/datasets/aditya126/movies-box-office-dataset-2000-2024) — descartado após confirmar bilheteria nativa no maricinnamon
- [mkrehage/harry-potter-books-and-movies-dataset](https://www.kaggle.com/datasets/mkrehage/harry-potter-books-and-movies-dataset) — substituído por adnananam + maricinnamon

## Status

| Fonte | Status |
|---|---|
| maricinnamon (6 tabelas) | ✅ Carregado |
| Books | ✅ Carregado |
| kornflex | ⬜ Pendente |
| HP-API | ⬜ Pendente |
| GSL (3 seeds) | ⬜ Pendente |
