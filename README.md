# Google Drive Downloader

Ferramenta para baixar arquivos e pastas públicos do Google Drive, com interface gráfica e linha de comando. Desenvolvida para uso no Windows.

## Funcionalidades

- Download de **arquivos** individuais do Google Drive
- Download de **pastas inteiras** (requer Google API Key)
- Interface **gráfica** (janela visual) e **terminal** (linha de comando)
- Barra de progresso com velocidade, tamanho e tempo estimado
- Limite de velocidade de download configurável
- Retomada de downloads interrompidos
- Histórico de downloads em arquivo de log

## Requisitos

- Python 3.8 ou superior
- Windows 10/11

## Instalação

```bash
# Clone o repositório
git clone https://github.com/danielfranca47/gdrive-downloader.git
cd gdrive-downloader

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

## Como usar

### Interface gráfica

```bash
python main.py --gui
```

### Linha de comando

```bash
# Baixar um arquivo
python main.py "https://drive.google.com/file/d/ID/view" -o "C:\Downloads"

# Baixar uma pasta (requer API Key)
python main.py "https://drive.google.com/drive/folders/ID" -o "C:\Downloads" --api-key "SUA_CHAVE"
```

### Opções disponíveis

| Opção | Descrição |
|-------|-----------|
| `--gui` | Abre a interface gráfica |
| `-o PASTA` | Pasta de destino para salvar os arquivos |
| `--api-key CHAVE` | Google API Key (necessária para pastas) |
| `--speed KB/S` | Limita a velocidade de download em KB/s |
| `--resume` | Retoma um download interrompido |
| `--no-color` | Remove cores do terminal |

## Google API Key (necessária para pastas)

O Google bloqueia ferramentas automáticas ao baixar pastas. Para contornar isso, o programa usa a Google Drive API gratuita.

Para obter sua chave:
1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto e ative a **Google Drive API**
3. Crie uma **Chave de API** em "Credenciais"

A chave é **gratuita** e permite até 1.000 downloads por dia.

Consulte o [guia-de-uso.md](guia-de-uso.md) para instruções detalhadas passo a passo.

## Dependências

| Pacote | Uso |
|--------|-----|
| `gdown` | Download de arquivos/pastas do Google Drive |
| `tqdm` | Barra de progresso no terminal |
| `colorama` | Cores no terminal Windows |

## Logs

Todos os downloads são registrados automaticamente em:
```
logs/gdrive_downloader.log
```

## Licença

MIT
