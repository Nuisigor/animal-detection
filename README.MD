# Animal Finder

## Pré-requisitos

Para utilizar este aplicativo, é necessário ter o Python na versão 3.10 ou superior instalado em sua máquina. Verifique a versão do Python instalada com os comandos abaixo:

```bash

python  --version

```

ou

```bash

python3  --version

```

## Instalação das bibliotecas

Para a instalação das bibliotecas apenas é necessário instalar os pacotes através do arquivo `requirements.txt`. Isto pode ser feito criando um ambiente virtual Python, ou diretamente pelo usuário do computador.

### Criando e Ativando um Ambiente Virtual

#### Windows (Powershell)

1. Crie o ambiente virtual:

```bash

python -m venv nome_do_ambiente

```

2. Ative o ambiente virtual:

```bash

.\nome_do_ambiente\Scripts\Activate.ps1

```

3. Instale as bibliotecas listadas no `requirements.txt`:

```bash

pip install -r requirements.txt

```

#### Linux / macOS

1. Crie o ambiente virtual:

```bash

python3 -m venv nome_do_ambiente

```

2. Ative o ambiente virtual:

```bash

source ./nome_do_ambiente/bin/activate

```

3. Instale as bibliotecas listadas no `requirements.txt`:

```bash

pip install -r requirements.txt

```

### Instalação Global (Não Recomendado)

Caso prefira instalar as bibliotecas diretamente no sistema (o que não é recomendado, pois pode causar conflitos com outras bibliotecas instaladas), use o seguinte comando:

```bash

pip  install  -r  requirements.txt

```

## Utilização

Para utilizar o aplicativo, execute o arquivo `main.py` da seguinte forma:

### Windows

```bash

python  main.py

```

### Linux / macOS

```bash

python3  main.py

```
