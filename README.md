# Blockbet - Api

Blockbet é um site de apostas que utiliza a tecnologia blockchain como ferramenta de iteração, gerando maior segurança e confiabilidade nas transações.

### Requisitos para execução do projeto (Api):

```
node
yarn
```

### Como executar:

1 - Inicializar o nó da Cartesi:
Primeiro, foi necessário instalar a biblioteca sunodo, com o seguinte comando: 
```
npm install -g @sunodo/cli
```

2 - Assim, após a instalação, para inicialização do nó é necessário utilizar dois comandos do sunodo e estar com o Docker aberto:
```
sunodo build
```
e
```
sunodo run --no-backend
```

3 - Após a inicialização do nó, é necessário executar a api , assim, as seguintes linhas de código deverão ser executadas:

```
cd<nome do projeto>
```
```
python3 -m venv .venv
```
```
. .venv/bin/activate
```
```
 pip install -r requirements.txt
```
```
python3 dapp.py
```


# Frontend

O projeto de frontend está disponível no endereço: https://github.com/jsimonassi/Blockbet


# Alunos
Gustavo Luppi Siloto

João Victor Simonassi

Professor: Antonio Augusto de Aragao Rocha

Disciplina: TCC00274 - TÓPICOS EM REDES DE COMPUTADORES I - B1

2023 / 2º
