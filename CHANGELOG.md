# Changelog - Novas Funcionalidades Download CAR

## 🆕 Versão 2.0.0 - Novas Funcionalidades

### ✅ Mudanças Implementadas

#### Backend (app.py)

1. **Polígono Padrão Alterado**
   - ❌ **Removido**: `APPS` como polígono padrão
   - ✅ **Adicionado**: `AREA_IMOVEL` como polígono padrão
   - 📍 **Localização**: Todos os endpoints `/download_state` e `/download_country`

2. **Endpoint `/estado` Renomeado**
   - ❌ **Removido**: Endpoint `/estado`
   - ✅ **Adicionado**: Endpoint `/state` (mesma funcionalidade)
   - 🔧 **Melhorias**: 
     - Parâmetro opcional `state` para limitar busca
     - Busca em todos os estados se não especificado

3. **Novo Endpoint `/property`**
   - ✅ **Adicionado**: Endpoint para download de propriedade específica
   - 📋 **Parâmetros**:
     - `car` (obrigatório): Número do CAR
     - `state` (opcional): Sigla do estado
     - `data_folder` (opcional): Pasta de dados
   - 📦 **Retorno**: Shape da propriedade em formato ZIP

4. **Parâmetros Opcionais**
   - ✅ **Modificado**: Parâmetro `folder` não é mais obrigatório
   - ✅ **Adicionado**: Polígono padrão `AREA_IMOVEL` em todos os endpoints

#### Frontend (index.html)

1. **Tabela Atualizada**
   - ❌ **Removida**: Coluna "Diretório"
   - ✅ **Adicionadas**: 
     - Coluna "Polígono" - Seletor dropdown
     - Coluna "CAR" - Campo de texto
     - Coluna "Propriedade" - Link de download

2. **Comportamento dos Campos**

   **Campo Polígono:**
   - ✅ Dropdown com todas as opções disponíveis
   - ✅ Valor padrão: `AREA_IMOVEL`
   - ✅ Persistido no localStorage

   **Campo CAR:**
   - ✅ Habilitado apenas quando estado baixado com sucesso
   - ✅ Desabilitado se não baixado ou erro registrado
   - ✅ Persistido no localStorage

   **Campo Propriedade:**
   - ✅ Habilitado quando estado baixado E CAR informado
   - ✅ Desabilitado se não baixado o shape ou erro
   - ✅ Link para download do shape da propriedade

3. **Novas Funções JavaScript**
   - ✅ `updatePolygon(estado, value)` - Atualiza polígono
   - ✅ `updateCar(estado, value)` - Atualiza código CAR
   - ✅ `downloadProperty(estado, car)` - Download da propriedade
   - ✅ `getPropertyLink(estado, history)` - Gera link da propriedade

#### Configurações

1. **Docker Compose**
   - ✅ Adicionada variável `POLYGON=AREA_IMOVEL`

2. **Scripts**
   - ✅ `entrypoint.download.sh`: Polígono padrão `AREA_IMOVEL`
   - ✅ `download_state.py`: Polígono padrão `AREA_IMOVEL`

3. **Makefile**
   - ✅ Novo comando: `make search-car car=CODIGO`
   - ✅ Novo comando: `make download-property car=CODIGO`

4. **Configuração**
   - ✅ `config.env`: Adicionada `DEFAULT_POLYGON=AREA_IMOVEL`

#### Arquivos Criados

1. **Documentação**
   - ✅ `README_NEW_FEATURES.md` - Documentação completa
   - ✅ `CHANGELOG.md` - Este arquivo

2. **Testes**
   - ✅ `test_new_features.sh` - Script de teste das funcionalidades

### 🔧 Compatibilidade

- ✅ **Preservadas**: Todas as funcionalidades existentes
- ✅ **Mantido**: Layout original da interface
- ✅ **Adicionadas**: Novas funcionalidades sem quebrar o existente
- ✅ **Alterado**: Apenas o polígono padrão de `APPS` para `AREA_IMOVEL`

### 🧪 Testes

- ✅ Sintaxe do `app.py` verificada
- ✅ HTML carregado com sucesso
- ✅ Script de teste criado
- ✅ Documentação completa

### 📋 Checklist Final

- [x] Polígono padrão alterado para `AREA_IMOVEL`
- [x] Coluna "Diretório" ocultada
- [x] Nova coluna "Polígono" adicionada
- [x] Nova coluna "CAR" adicionada
- [x] Nova coluna "Propriedade" adicionada
- [x] Endpoint `/estado` renomeado para `/state`
- [x] Novo endpoint `/property` criado
- [x] Comportamento dos campos implementado
- [x] Configurações atualizadas
- [x] Documentação criada
- [x] Scripts de teste criados

### 🚀 Próximos Passos

1. Testar as funcionalidades em ambiente de desenvolvimento
2. Verificar se todos os endpoints estão funcionando
3. Validar o comportamento da interface web
4. Executar testes de integração
5. Fazer deploy em produção

---

**Data**: $(date)
**Versão**: 2.0.0
**Status**: ✅ Implementado 