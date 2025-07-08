# 📥 Download CAR - Google Colab

Este documento explica como usar o notebook `colab_download_car.ipynb` para baixar arquivos do Cadastro Ambiental Rural (SICAR) diretamente no Google Colab.

## 🎯 Objetivo

O notebook `colab_download_car.ipynb` foi criado para permitir que usuários baixem arquivos do SICAR sem precisar configurar um ambiente local ou usar Docker. Tudo é executado diretamente no navegador através do Google Colab.

## 🚀 Como Usar

### 1. Acessar o Notebook

1. Abra o [Google Colab](https://colab.research.google.com/)
2. Faça upload do arquivo `colab_download_car.ipynb` ou clone o repositório
3. Ou use o link direto: [![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Malnati/download-car/blob/main/colab_download_car.ipynb)

### 2. Configurar Parâmetros

Na seção **"⚙️ Configuração dos Parâmetros"**, configure:

```python
# Estado a ser baixado
ESTADO = "SP"  # Exemplos: "SP", "RJ", "MG", "PA", "DF", etc.

# Tipo de polígono
POLIGONO = "APPS"  # Exemplos: "APPS", "AREA_PROPERTY", "LEGAL_RESERVE", etc.

# Pasta de destino (opcional)
PASTA_DESTINO = ""  # Deixe vazio para pasta padrão

# Configurações avançadas
TENTATIVAS = 25      # Número máximo de tentativas
TIMEOUT = 30         # Timeout em segundos
DEBUG = False        # Modo debug
DRIVER = "Tesseract" # Driver OCR: "Tesseract" ou "Paddle"
```

### 3. Executar as Células

Execute as células na seguinte ordem:

1. **Montar Google Drive** (opcional) - Para salvar arquivos permanentemente
2. **Instalar Dependências** - Instala o pacote download-car
3. **Importar Bibliotecas** - Importa as classes necessárias
4. **Configurar Parâmetros** - Define os parâmetros de download
5. **Validar Parâmetros** - Verifica se os parâmetros são válidos
6. **Executar Download** - Inicia o processo de download
7. **Verificar Arquivos** - Lista os arquivos baixados
8. **Criar ZIP** - Cria um arquivo ZIP com os dados
9. **Download ZIP** - Baixa o arquivo ZIP para o computador

## 📋 Estados Disponíveis

| Sigla | Estado |
|-------|--------|
| AC | Acre |
| AL | Alagoas |
| AM | Amazonas |
| AP | Amapá |
| BA | Bahia |
| CE | Ceará |
| DF | Distrito Federal |
| ES | Espírito Santo |
| GO | Goiás |
| MA | Maranhão |
| MG | Minas Gerais |
| MS | Mato Grosso do Sul |
| MT | Mato Grosso |
| PA | Pará |
| PB | Paraíba |
| PE | Pernambuco |
| PI | Piauí |
| PR | Paraná |
| RJ | Rio de Janeiro |
| RN | Rio Grande do Norte |
| RO | Rondônia |
| RR | Roraima |
| RS | Rio Grande do Sul |
| SC | Santa Catarina |
| SE | Sergipe |
| SP | São Paulo |
| TO | Tocantins |

## 🗺️ Polígonos Disponíveis

| Código | Descrição |
|--------|-----------|
| `APPS` | Área de Preservação Permanente |
| `AREA_PROPERTY` | Perímetros dos imóveis |
| `NATIVE_VEGETATION` | Remanescente de Vegetação Nativa |
| `CONSOLIDATED_AREA` | Área Consolidada |
| `AREA_FALL` | Área de Pousio |
| `HYDROGRAPHY` | Hidrografia |
| `RESTRICTED_USE` | Uso Restrito |
| `ADMINISTRATIVE_SERVICE` | Servidão Administrativa |
| `LEGAL_RESERVE` | Reserva Legal |

## 🔧 Configurações Avançadas

### Drivers OCR

- **Tesseract** (padrão): Mais rápido, funciona bem para a maioria dos casos
- **Paddle**: Mais preciso, pode ser necessário para captchas complexos

### Parâmetros de Rede

- **TENTATIVAS**: Número máximo de tentativas em caso de falha (padrão: 25)
- **TIMEOUT**: Tempo máximo em segundos para cada tentativa (padrão: 30)
- **DEBUG**: Modo debug para informações detalhadas (padrão: False)

## 📁 Estrutura de Arquivos

O notebook cria a seguinte estrutura:

```
temp/ESTADO/
├── dados.shp
├── dados.shx
├── dados.dbf
└── dados.prj
```

E também gera um arquivo ZIP com timestamp:
```
ESTADO_POLIGONO_YYYYMMDD_HHMMSS.zip
```

## 💾 Salvamento de Arquivos

### Opção 1: Download Direto
- Os arquivos são baixados automaticamente para a pasta de downloads do navegador
- Funciona em qualquer navegador moderno

### Opção 2: Google Drive
- Monte o Google Drive na primeira célula
- Configure `PASTA_DESTINO = "drive/MyDrive/download-car/ESTADO"`
- Os arquivos ficam salvos permanentemente no seu Drive

## ⚠️ Limitações e Considerações

1. **Tempo de Execução**: Downloads podem levar vários minutos dependendo do tamanho dos dados
2. **Limite de Memória**: O Colab tem limites de memória e tempo de execução
3. **Conexão**: Requer conexão estável com a internet
4. **Captcha**: O sistema pode solicitar resolução de captcha automaticamente

## 🐛 Solução de Problemas

### Erro de Instalação
```bash
# Se houver problemas com dependências
!pip install --upgrade pip
!pip install git+https://github.com/Malnati/download-car --force-reinstall
```

### Erro de Driver OCR
```python
# Tente alternar entre drivers
DRIVER = "Paddle"  # Em vez de "Tesseract"
```

### Timeout
```python
# Aumente o timeout se necessário
TIMEOUT = 60  # Em vez de 30
```

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/Malnati/download-car/issues)
- **Documentação**: [README Principal](README.md)
- **Email**: ricardomalnati@gmail.com

## 🔄 Atualizações

O notebook é atualizado regularmente para:
- Melhorar a compatibilidade com o Google Colab
- Adicionar novos recursos
- Corrigir bugs e problemas conhecidos

## 📄 Licença

Este notebook segue a mesma licença do projeto principal: [MIT](LICENSE)

---

**Nota**: Este notebook é uma extensão do projeto download-car e mantém total compatibilidade com a API e CLI existentes. 