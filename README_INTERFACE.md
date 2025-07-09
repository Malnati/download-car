# Interface Web - Download CAR

## 📋 Visão Geral

Esta interface web permite gerenciar downloads de dados do Cadastro Ambiental Rural (CAR) para todos os estados brasileiros de forma intuitiva e responsiva.

## 🚀 Como Acessar

### Via Docker (Recomendado)
```bash
# Acesse a interface através do nginx
http://localhost:8787
```

### Via Desenvolvimento Local
```bash
# Abra o arquivo index.html diretamente no navegador
# ou use um servidor local
python -m http.server 8080
# Acesse: http://localhost:8080
```

## 🎨 Características da Interface

### ✨ Design Responsivo
- **Cores da EMBRAPA**: Verde institucional (#2E7D32, #4CAF50, #1B5E20)
- **Bootstrap 5.4.0**: Framework CSS moderno e responsivo
- **Font Awesome**: Ícones profissionais
- **Google Fonts**: Tipografia Inter para melhor legibilidade

### 🏁 Bandeiras dos Estados
- Todas as 27 bandeiras dos estados brasileiros
- Carregamento via CDN (Wikimedia Commons)
- Fallback para placeholder em caso de erro

### 📊 Tabela Interativa
| Coluna | Descrição | Funcionalidade |
|--------|-----------|----------------|
| **Estado** | Bandeira + Sigla | Exibição visual com bandeira |
| **Diretório** | Sigla do estado | Código do diretório destino |
| **Espera (s)** | Timeout em segundos | Campo editável (10-300s) |
| **Tentativas** | Máximo de retry | Campo editável (1-20) |
| **Última** | Data/hora último download | Formato: yyyy-MM-dd HH:mm |
| **Status** | Ícone de status | ✅ Sucesso / ❌ Erro / ⏳ Pendente |
| **Ação** | Botão de download | Executa download via API |

## ⚙️ Configuração

### URL da API
- **Campo editável** no topo da página
- **Valor padrão**: `http://localhost:8000` (local) ou `/api` (via nginx)
- **Botão "Testar Conexão"** para verificar conectividade

### Parâmetros por Estado
- **Timeout**: Tempo máximo de espera por tentativa (10-300 segundos)
- **Tentativas**: Número máximo de retentativas (1-20)
- **Persistência**: Valores salvos no localStorage do navegador

## 🔧 Funcionalidades

### 📥 Download de Estados
1. **Clique no botão "Download"** de qualquer estado
2. **Parâmetros automáticos**:
   - Estado: Sigla do estado selecionado
   - Polígono: APPS (padrão)
   - Timeout: Valor configurado na tabela
   - Max Retries: Valor configurado na tabela
   - Debug: false

3. **Processo de download**:
   - Botão mostra spinner durante download
   - Arquivo ZIP baixado automaticamente
   - Status atualizado na tabela
   - Notificação de sucesso/erro

### 📊 Histórico de Downloads
- **Data/hora** do último download
- **Status** visual (ícones coloridos)
- **Persistência** no localStorage
- **Atualização automática** da interface

### 🔔 Notificações
- **Toast notifications** no canto superior direito
- **Cores por tipo**: Verde (sucesso), Vermelho (erro), Azul (info)
- **Auto-dismiss** após alguns segundos

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilos customizados com variáveis CSS
- **JavaScript ES6+**: Funcionalidades interativas
- **Bootstrap 5.4.0**: Framework CSS responsivo
- **Font Awesome 6.4.0**: Biblioteca de ícones

### CDNs Utilizados
```html
<!-- Bootstrap -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.0/dist/css/bootstrap.min.css">

<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- Bandeiras dos Estados -->
<!-- Via Wikimedia Commons CDN -->
```

### Backend Integration
- **API REST**: Integração com FastAPI
- **FormData**: Envio de parâmetros via POST
- **Blob Download**: Download automático de arquivos ZIP
- **Error Handling**: Tratamento de erros da API

## 📱 Responsividade

### Breakpoints
- **Desktop**: > 768px - Layout completo
- **Tablet**: 768px - Tabela responsiva
- **Mobile**: < 768px - Elementos redimensionados

### Adaptações Mobile
- **Fonte menor** na tabela
- **Bandeiras menores** (20x14px)
- **Botões compactos**
- **Scroll horizontal** na tabela

## 🎯 Cores EMBRAPA

```css
:root {
    --embrapa-green: #2E7D32;        /* Verde principal */
    --embrapa-light-green: #4CAF50;  /* Verde claro */
    --embrapa-dark-green: #1B5E20;   /* Verde escuro */
    --embrapa-yellow: #FFC107;       /* Amarelo */
    --embrapa-orange: #FF9800;       /* Laranja */
    --embrapa-red: #F44336;          /* Vermelho */
    --embrapa-gray: #757575;         /* Cinza */
    --embrapa-light-gray: #F5F5F5;   /* Cinza claro */
}
```

## 🔄 Estados de Download

### Status Icons
- ✅ **Sucesso**: `fa-check-circle` (verde)
- ❌ **Erro**: `fa-times-circle` (vermelho)
- ⏳ **Pendente**: `fa-clock` (laranja)
- ➖ **Nenhum**: `fa-minus` (cinza)

### Estados do Botão
- **Normal**: "Download" com ícone
- **Carregando**: Spinner + "Baixando..."
- **Desabilitado**: Durante download

## 📝 Exemplo de Uso

1. **Acesse** `http://localhost:8787`
2. **Configure** a URL da API (se necessário)
3. **Ajuste** timeout e tentativas para cada estado
4. **Clique** em "Download" para qualquer estado
5. **Aguarde** o download automático do arquivo ZIP
6. **Monitore** o status na tabela

## 🐛 Troubleshooting

### Problemas Comuns
1. **API não responde**: Verifique se a API está rodando
2. **Bandeiras não carregam**: Verifique conexão com internet
3. **Download falha**: Verifique parâmetros de timeout/tentativas
4. **Interface não carrega**: Verifique se o nginx está rodando

### Logs
- **Console do navegador**: Para erros JavaScript
- **Logs do Docker**: `docker-compose logs`
- **Logs da API**: `docker-compose logs download-car-api`

## 🔮 Próximas Melhorias

- [ ] Seleção de tipo de polígono por estado
- [ ] Download em lote (múltiplos estados)
- [ ] Gráficos de progresso
- [ ] Exportação de histórico
- [ ] Configurações avançadas
- [ ] Tema escuro
- [ ] PWA (Progressive Web App) 