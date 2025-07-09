# 🆕 Novas Funcionalidades - Download CAR

Este documento descreve as novas funcionalidades implementadas no sistema Download CAR.

## 📋 Resumo das Mudanças

### Backend (app.py)

#### 1. Polígono Padrão Alterado
- **Antes**: `APPS` era o polígono padrão
- **Agora**: `AREA_IMOVEL` é o polígono padrão para todos os endpoints

#### 2. Endpoint `/estado` Renomeado
- **Antes**: `/estado` - Busca estado de um imóvel pelo CAR
- **Agora**: `/state` - Mesma funcionalidade, mas com nome em inglês
- **Melhorias**: 
  - Adicionado parâmetro opcional `state` para limitar a busca
  - Busca em todos os estados se não especificado

#### 3. Novo Endpoint `/property`
- **Funcionalidade**: Busca uma propriedade específica pelo número do CAR
- **Retorno**: Shape da propriedade encontrada em formato ZIP
- **Parâmetros**:
  - `car` (obrigatório): Número do CAR da propriedade
  - `state` (opcional): Sigla do estado para limitar a busca
  - `data_folder` (opcional): Pasta com os dados baixados

#### 4. Parâmetros Opcionais
- O parâmetro `folder` não é mais obrigatório nos endpoints
- Polígono padrão definido como `AREA_IMOVEL`

### Frontend (index.html)

#### 1. Tabela Atualizada
- **Removida**: Coluna "Diretório"
- **Adicionadas**: 
  - Coluna "Polígono" - Seletor de tipo de polígono
  - Coluna "CAR" - Campo para informar código CAR
  - Coluna "Propriedade" - Link para download da propriedade

#### 2. Comportamento dos Campos

##### Campo Polígono
- Dropdown com todas as opções de polígonos disponíveis
- Valor padrão: `AREA_IMOVEL`
- Persistido no localStorage

##### Campo CAR
- Campo de texto para informar código CAR
- **Habilitado**: Apenas quando o estado foi baixado com sucesso
- **Desabilitado**: Se não baixado ou erro registrado
- Persistido no localStorage

##### Campo Propriedade
- **Habilitado**: Quando estado baixado com sucesso E CAR informado
- **Desabilitado**: Se não baixado o shape do estado ou erro registrado
- **Funcionalidade**: Link para download do shape da propriedade

#### 3. Novas Funções JavaScript
- `updatePolygon(estado, value)` - Atualiza polígono selecionado
- `updateCar(estado, value)` - Atualiza código CAR
- `downloadProperty(estado, car)` - Download da propriedade
- `getPropertyLink(estado, history)` - Gera link da propriedade

### Configurações Atualizadas

#### 1. Docker Compose
- Adicionada variável de ambiente `POLYGON=AREA_IMOVEL`

#### 2. Scripts
- `entrypoint.download.sh`: Polígono padrão alterado para `AREA_IMOVEL`
- `download_state.py`: Polígono padrão alterado para `AREA_IMOVEL`

#### 3. Makefile
- Novos comandos:
  - `make search-car car=SP12345678901234567890` - Busca estado do CAR
  - `make download-property car=SP12345678901234567890` - Download da propriedade

#### 4. Configuração
- `config.env`: Adicionada `DEFAULT_POLYGON=AREA_IMOVEL`

## 🚀 Como Usar

### 1. Download com Polígono Padrão
```bash
# Download automático com AREA_IMOVEL
curl -X POST "http://localhost:8000/download_state" \
  -F "state=SP" \
  --output SP_AREA_IMOVEL.zip
```

### 2. Busca por CAR
```bash
# Buscar estado de um imóvel
curl -X GET "http://localhost:8000/state?car=SP12345678901234567890"

# Buscar em estado específico
curl -X GET "http://localhost:8000/state?car=SP12345678901234567890&state=SP"
```

### 3. Download de Propriedade
```bash
# Download da propriedade
curl -X GET "http://localhost:8000/property?car=SP12345678901234567890" \
  --output property_SP12345678901234567890.zip

# Download de propriedade em estado específico
curl -X GET "http://localhost:8000/property?car=SP12345678901234567890&state=SP" \
  --output property_SP12345678901234567890.zip
```

### 4. Interface Web
1. Acesse a interface em `http://localhost:8787`
2. Selecione o polígono desejado na coluna "Polígono"
3. Clique em "Requisitar" para baixar o estado
4. Após sucesso, informe o código CAR na coluna "CAR"
5. Clique em "Propriedade" para baixar o shape da propriedade

## 🧪 Testes

Execute o script de teste para verificar as funcionalidades:

```bash
./test_new_features.sh
```

## 📝 Observações

- Todas as funcionalidades existentes foram preservadas
- Apenas o polígono padrão foi alterado de `APPS` para `AREA_IMOVEL`
- O endpoint `/estado` foi renomeado para `/state` (mantendo compatibilidade)
- Novas funcionalidades foram adicionadas sem modificar o comportamento existente
- Interface mantém o layout original, apenas adicionando as novas colunas solicitadas 