# Guia de Uso — Google Drive Downloader

Este guia explica como instalar e usar o programa para baixar arquivos e pastas do Google Drive.  
Não é necessário ter conhecimento de programação — siga os passos na ordem.

---

## Índice

1. [Antes de começar — Instalar o Python](#1-antes-de-começar--instalar-o-python)
2. [Configuração inicial — Fazer apenas uma vez](#2-configuração-inicial--fazer-apenas-uma-vez)
3. [Como obter o link do Google Drive](#3-como-obter-o-link-do-google-drive)
4. [Google API Key — necessária para pastas](#4-google-api-key--necessária-para-pastas)
5. [Usando a interface gráfica (janela)](#5-usando-a-interface-gráfica-janela)
6. [Usando o terminal (linha de comando)](#6-usando-o-terminal-linha-de-comando)
7. [Onde ficam os arquivos baixados](#7-onde-ficam-os-arquivos-baixados)
8. [Consultando o histórico de downloads](#8-consultando-o-histórico-de-downloads)
9. [Solução de problemas comuns](#9-solução-de-problemas-comuns)

---

## 1. Antes de começar — Instalar o Python

O programa é feito em Python. Se você ainda não tem o Python instalado no computador, siga os passos abaixo.

### Como verificar se o Python já está instalado

1. Pressione as teclas **Windows + R** ao mesmo tempo
2. Digite `cmd` e pressione **Enter** — uma janela preta vai abrir
3. Digite o comando abaixo e pressione **Enter**:
   ```
   python --version
   ```
4. Se aparecer algo como `Python 3.11.0` (qualquer versão 3.8 ou superior), o Python já está instalado. Pule para o passo 2.
5. Se aparecer uma mensagem de erro, o Python não está instalado — continue lendo.

### Como instalar o Python

1. Abra o navegador e acesse: **https://www.python.org/downloads/**
2. Clique no botão grande escrito **"Download Python 3.x.x"**
3. Aguarde o download e abra o arquivo baixado
4. **IMPORTANTE:** Na primeira tela do instalador, marque a caixa que diz **"Add Python to PATH"** antes de clicar em instalar

   ```
   ┌─────────────────────────────────────────────┐
   │  Install Python 3.x.x                       │
   │                                             │
   │  [✓] Add Python to PATH  ← MARQUE ISSO     │
   │                                             │
   │  [ Install Now ]                            │
   └─────────────────────────────────────────────┘
   ```

5. Clique em **"Install Now"** e aguarde a instalação terminar
6. Clique em **"Close"** quando aparecer "Setup was successful"
7. Feche e reabra o terminal (janela preta) e repita o teste do passo anterior para confirmar

---

## 2. Configuração inicial — Fazer apenas uma vez

Esta etapa instala as ferramentas necessárias para o programa funcionar. **Você só precisa fazer isso uma vez.**

### Passo a passo

1. Pressione **Windows + R**, digite `cmd` e pressione **Enter**
2. Navegue até a pasta do programa digitando o comando abaixo e pressionando **Enter**:
   ```
   cd C:\automacao_google_drive
   ```
3. Crie o ambiente virtual digitando e pressionando **Enter**:
   ```
   python -m venv venv
   ```
   > Aguarde alguns segundos. Uma pasta chamada `venv` será criada.

4. Ative o ambiente virtual:
   ```
   venv\Scripts\activate
   ```
   > A linha do terminal vai mudar e mostrar `(venv)` no início — isso significa que funcionou.
   >
   > Exemplo de como vai ficar: `(venv) C:\automacao_google_drive>`

5. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
   > Aguarde o download e instalação. Pode levar 1 a 2 minutos dependendo da sua internet.
   > Quando terminar, vai aparecer a mensagem: `Successfully installed ...`

**Pronto! A configuração está completa.**

---

## 3. Como obter o link do Google Drive

O programa aceita links de **arquivos** e **pastas** do Google Drive, desde que estejam configurados como **"Qualquer pessoa com o link"**.

### Obtendo o link de um arquivo

1. Acesse o Google Drive no navegador
2. Clique com o **botão direito** no arquivo que deseja baixar
3. Clique em **"Compartilhar"**
4. Em "Acesso geral", clique em **"Restrito"** e mude para **"Qualquer pessoa com o link"**
5. Clique em **"Copiar link"**
6. Clique em **"Concluído"**

O link copiado vai parecer com este exemplo:
```
https://drive.google.com/file/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/view?usp=sharing
```

### Obtendo o link de uma pasta

1. Acesse o Google Drive no navegador
2. Clique com o **botão direito** na pasta que deseja baixar
3. Clique em **"Compartilhar"**
4. Em "Acesso geral", clique em **"Restrito"** e mude para **"Qualquer pessoa com o link"**
5. Clique em **"Copiar link"**
6. Clique em **"Concluído"**

O link copiado vai parecer com este exemplo:
```
https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ?usp=sharing
```

> **Atenção:** O programa **não funciona** com arquivos ou pastas privados (que precisam de login). O compartilhamento deve ser "Qualquer pessoa com o link".

---

## 4. Google API Key — necessária para pastas

O Google passou a bloquear ferramentas automáticas que tentam baixar pastas compartilhadas, mesmo quando a pasta está configurada como pública. Por isso, o programa agora usa a **Google Drive API**, que é gratuita e não tem essa restrição.

> **Baixar arquivos individuais** continua funcionando sem API Key.  
> **Baixar pastas** requer a API Key configurada conforme os passos abaixo.

### Como obter a Google API Key (gratuito)

Este processo leva cerca de 5 minutos e precisa ser feito **apenas uma vez**.

**Passo 1 — Acesse o Google Cloud Console**

1. Abra o navegador e acesse: **https://console.cloud.google.com**
2. Entre com a sua conta Google normalmente

**Passo 2 — Crie um projeto**

1. No canto superior esquerdo, clique no seletor de projetos (ao lado do logo do Google Cloud)
2. Clique em **"Novo projeto"**
3. Dê qualquer nome (ex: `gdrive-downloader`) e clique em **"Criar"**
4. Aguarde alguns segundos e selecione o projeto recém-criado

**Passo 3 — Ative a Google Drive API**

1. No menu lateral esquerdo, clique em **"APIs e serviços"** → **"Biblioteca"**
2. Na barra de pesquisa, digite `Google Drive API`
3. Clique no resultado **"Google Drive API"**
4. Clique no botão azul **"Ativar"**
5. Aguarde a ativação (alguns segundos)

**Passo 4 — Crie a chave de API**

1. No menu lateral, clique em **"APIs e serviços"** → **"Credenciais"**
2. Clique em **"Criar credenciais"** (botão no topo)
3. Selecione **"Chave de API"**
4. Uma janela vai exibir a chave gerada — ela tem este formato:
   ```
   AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
5. Clique em **"Copiar"** para copiar a chave
6. Clique em **"Fechar"**

> A chave gerada é **gratuita** e permite até **1.000 downloads por dia**, o que é mais do que suficiente para uso normal.

### Como configurar a chave no programa

- **Interface gráfica:** Cole a chave no campo **"Google API Key"** antes de clicar em Baixar. O programa salva automaticamente — você não precisa colar de novo nas próximas vezes.
- **Terminal:** Use a opção `--api-key "SUA_CHAVE"` no comando. Veja exemplos na [seção 6](#6-usando-o-terminal-linha-de-comando).

---

## 5. Usando a interface gráfica (janela)

Esta é a forma mais fácil de usar o programa — abre uma janela visual.

### Abrindo o programa

1. Pressione **Windows + R**, digite `cmd` e pressione **Enter**
2. Navegue até a pasta do programa:
   ```
   cd C:\automacao_google_drive
   ```
3. Ative o ambiente virtual:
   ```
   venv\Scripts\activate
   ```
4. Abra a janela gráfica:
   ```
   python main.py --gui
   ```

Uma janela como esta vai abrir:

```
┌──────────────────────────────────────────────────────┐
│  Google Drive Downloader                             │
│  Downloads de links públicos do Google Drive         │
├──────────────────────────────────────────────────────┤
│  Link do Drive:    [________________________________] │
│  Pasta de destino: [____________________] [Procurar] │
│  Google API Key:   [____________________]         [?]│
│  Velocidade máxima: [______] KB/s  [ ] Retomar       │
│                                                      │
│               [  ⬇  Baixar  ]                        │
├──────────────────────────────────────────────────────┤
│  Progresso: [░░░░░░░░░░░░░░░░░░░░░░░░]               │
│  Status: Aguardando...                               │
├──────────────────────────────────────────────────────┤
│  Log:                                                │
│  ┌────────────────────────────────────────────────┐  │
│  │                                                │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Como usar a janela

**Passo 1 — Cole o link do Drive**
- Clique no campo ao lado de **"Link do Drive:"**
- Cole o link copiado do Google Drive (use **Ctrl+V**)

**Passo 2 — Escolha onde salvar**
- Clique no botão **"Procurar"**
- Uma janela de seleção de pastas vai abrir
- Navegue até a pasta onde quer salvar os arquivos (ex: `Documentos`, `Downloads`, etc.)
- Clique em **"Selecionar pasta"**

**Passo 3 — Informe a Google API Key (necessário para pastas)**
- Cole a sua API Key no campo **"Google API Key"**
- O programa salva a chave automaticamente — nas próximas vezes o campo já estará preenchido
- Para saber como obter a chave, clique no botão **"?"** ao lado do campo ou consulte a [seção 4](#4-google-api-key--necessária-para-pastas)

**Passo 4 — Opções extras (opcional)**
- **Velocidade máxima:** Se quiser limitar a velocidade de download, digite um número em KB/s (ex: `512` para meio megabyte por segundo). Deixe em branco para baixar na velocidade máxima.
- **Retomar download interrompido:** Marque esta caixa se um download anterior foi interrompido e você quer continuar de onde parou.

**Passo 5 — Clique em Baixar**
- Clique no botão **"⬇ Baixar"**
- Acompanhe o progresso na barra e na área de log abaixo
- Quando terminar, uma mensagem de confirmação vai aparecer no log

> **Não feche a janela** enquanto o download estiver em andamento.

---

## 6. Usando o terminal (linha de comando)

Esta forma é útil para quem quer fazer downloads mais rápido, sem abrir a janela visual.

### Preparando o terminal

Antes de qualquer download pelo terminal, sempre faça estes dois passos:

1. Pressione **Windows + R**, digite `cmd` e pressione **Enter**
2. Digite:
   ```
   cd C:\automacao_google_drive
   ```
3. Digite:
   ```
   venv\Scripts\activate
   ```

### Baixar um arquivo

Use o comando abaixo, substituindo o link e o caminho da pasta:

```
python main.py "LINK_DO_ARQUIVO" -o "PASTA_DE_DESTINO"
```

**Exemplo real:**
```
python main.py "https://drive.google.com/file/d/1aBcXyZ/view?usp=sharing" -o "C:\Users\Daniel\Downloads"
```

### Baixar uma pasta inteira

Para pastas, é necessário informar a API Key com `--api-key`:

```
python main.py "LINK_DA_PASTA" -o "PASTA_DE_DESTINO" --api-key "SUA_CHAVE_AQUI"
```

**Exemplo real:**
```
python main.py "https://drive.google.com/drive/folders/1aBcXyZ?usp=sharing" -o "C:\Users\Daniel\Downloads\MinhaPasta" --api-key "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> Se não souber como obter a chave, consulte a [seção 4](#4-google-api-key--necessária-para-pastas).

### Opções extras

| Opção | O que faz | Exemplo |
|-------|-----------|---------|
| `--api-key "CHAVE"` | Define a Google API Key para download de pastas | `python main.py "LINK" -o "PASTA" --api-key "AIza..."` |
| `--speed 512` | Limita a velocidade para 512 KB/s | `python main.py "LINK" -o "PASTA" --speed 512` |
| `--resume` | Retoma um download interrompido | `python main.py "LINK" -o "PASTA" --resume` |
| `--no-color` | Remove as cores do terminal | `python main.py "LINK" -o "PASTA" --no-color` |
| `--help` | Mostra todas as opções disponíveis | `python main.py --help` |

### O que aparece durante o download

Durante o download, uma barra de progresso será exibida no terminal:

```
Iniciando download de arquivo:
  Origem:  https://drive.google.com/file/d/...
  Destino: C:\Users\Daniel\Downloads

video_aula.mp4
100%|████████████████████| 245M/245M [01:23<00:00, 2.94MB/s]

[OK] Download concluído em 1m 23s → C:\Users\Daniel\Downloads

  1 arquivo(s) salvo(s) em: C:\Users\Daniel\Downloads
  Log: logs/gdrive_downloader.log
```

A barra mostra:
- **Percentual** concluído
- **Tamanho** baixado / total
- **Tempo decorrido** e **tempo restante estimado**
- **Velocidade** atual em MB/s

---

## 7. Onde ficam os arquivos baixados

Os arquivos são salvos exatamente na pasta que você indicou.

- **Interface gráfica:** a pasta escolhida no campo "Pasta de destino"
- **Terminal:** o caminho após o `-o` no comando

**Exemplo:** se você usou `-o "C:\Users\Daniel\Downloads"`, os arquivos estarão em:
```
C:\
└── Users\
    └── Daniel\
        └── Downloads\
            └── nome_do_arquivo_baixado.mp4
```

Para pastas do Drive, será criada uma subpasta com o nome da pasta original:
```
C:\Users\Daniel\Downloads\
└── Nome da Pasta do Drive\
    ├── arquivo1.pdf
    ├── arquivo2.mp4
    └── arquivo3.docx
```

---

## 8. Consultando o histórico de downloads

Todos os downloads ficam registrados automaticamente em um arquivo de log.

### Como abrir o log

1. Abra o **Explorador de Arquivos** (Windows + E)
2. Navegue até `C:\automacao_google_drive\logs\`
3. Abra o arquivo `gdrive_downloader.log` com o Bloco de Notas

O arquivo vai conter registros como:
```
2026-04-08 21:30:00 [INFO] download: Download iniciado — arquivo | destino: C:\Downloads | url: https://...
2026-04-08 21:31:23 [INFO] download: Download concluído em 83.4s → C:\Downloads
```

Cada linha mostra:
- **Data e hora** do evento
- **Tipo** (INFO = normal, ERROR = erro)
- **Descrição** do que aconteceu

---

## 9. Solução de problemas comuns

### "python não é reconhecido como um comando"

**Causa:** O Python não está instalado ou não foi adicionado ao PATH.  
**Solução:** Desinstale o Python e reinstale seguindo o [Passo 1](#1-antes-de-começar--instalar-o-python), certificando-se de marcar **"Add Python to PATH"**.

---

### "venv\Scripts\activate não é reconhecido"

**Causa:** O ambiente virtual ainda não foi criado.  
**Solução:** Execute primeiro o comando de criação:
```
python -m venv venv
```
Depois ative normalmente:
```
venv\Scripts\activate
```

---

### "URL do Google Drive não reconhecida"

**Causa:** O link colado está incompleto ou não é um link válido do Google Drive.  
**Solução:**
- Certifique-se de copiar o link completo, começando com `https://drive.google.com/`
- Use as aspas ao redor do link no terminal: `"https://drive.google.com/..."`
- Verifique se copiou o link e não apenas o nome do arquivo

---

### O download começa mas para no meio

**Causa:** Queda de internet ou timeout do Google Drive.  
**Solução:** Execute o mesmo comando adicionando `--resume`:
```
python main.py "LINK" -o "PASTA" --resume
```
Isso vai retomar o download de onde parou.

---

### "Failed to retrieve file url" ou "gdown não conseguiu baixar a pasta"

**Causa:** O Google bloqueia ferramentas automáticas que tentam baixar pastas compartilhadas, mesmo quando a pasta é pública. Isso é uma limitação do Google, não do programa.  
**Solução:** Configure uma Google API Key conforme a [seção 4](#4-google-api-key--necessária-para-pastas) e informe-a no campo correspondente da interface ou com `--api-key` no terminal.

---

### A janela gráfica não abre

**Causa:** O ambiente virtual não está ativado.  
**Solução:** Certifique-se de ter ativado o ambiente antes de rodar o programa:
```
cd C:\automacao_google_drive
venv\Scripts\activate
python main.py --gui
```

---

### Preciso de ajuda com outro problema

Verifique o arquivo de log em `C:\automacao_google_drive\logs\gdrive_downloader.log` — ele contém mensagens detalhadas sobre o que aconteceu e pode ajudar a identificar o problema.
