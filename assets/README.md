# Assets - Recursos Estáticos

Esta pasta contém todos os recursos estáticos utilizados pela interface web do sistema Download CAR.

## 📁 Estrutura de Pastas

```
assets/
├── README.md          # Este arquivo
├── flags/             # Bandeiras dos estados brasileiros
│   ├── AC.svg         # Acre
│   ├── AL.svg         # Alagoas
│   ├── AM.svg         # Amazonas
│   ├── AP.svg         # Amapá
│   ├── BA.svg         # Bahia
│   ├── CE.svg         # Ceará
│   ├── DF.svg         # Distrito Federal
│   ├── ES.svg         # Espírito Santo
│   ├── GO.svg         # Goiás
│   ├── MA.svg         # Maranhão
│   ├── MG.svg         # Minas Gerais
│   ├── MS.svg         # Mato Grosso do Sul
│   ├── MT.svg         # Mato Grosso
│   ├── PA.svg         # Pará
│   ├── PB.svg         # Paraíba
│   ├── PE.svg         # Pernambuco
│   ├── PI.svg         # Piauí
│   ├── PR.svg         # Paraná
│   ├── RJ.svg         # Rio de Janeiro
│   ├── RN.svg         # Rio Grande do Norte
│   ├── RO.svg         # Rondônia
│   ├── RR.svg         # Roraima
│   ├── RS.svg         # Rio Grande do Sul
│   ├── SC.svg         # Santa Catarina
│   ├── SE.svg         # Sergipe
│   ├── SP.svg         # São Paulo
│   └── TO.svg         # Tocantins
```

## 🏁 Bandeiras dos Estados

### Formato
- **Formato**: SVG (Scalable Vector Graphics)
- **Dimensões**: 24x16 pixels (viewBox)
- **Qualidade**: Vetorial (escalável sem perda de qualidade)

### Características
- **27 bandeiras** dos estados brasileiros
- **Cores específicas** para cada estado
- **Design simplificado** com cores representativas
- **Texto da sigla** incluído na bandeira

### Cores por Estado
| Estado | Cores Principais | Descrição |
|--------|------------------|-----------|
| **SP** | Branco + Preto | Bandeira paulista |
| **RJ** | Branco + Azul | Bandeira carioca |
| **MG** | Branco + Vermelho | Bandeira mineira |
| **RS** | Vermelho + Amarelo | Bandeira gaúcha |
| **SC** | Vermelho + Branco | Bandeira catarinense |
| **PR** | Azul + Branco | Bandeira paranaense |
| **GO** | Verde + Amarelo | Bandeira goiana |
| **MT** | Vermelho + Verde | Bandeira mato-grossense |
| **MS** | Azul + Branco | Bandeira sul-mato-grossense |
| **DF** | Branco + Azul | Bandeira do Distrito Federal |
| **Outros** | Verde + Amarelo + Azul | Cores da bandeira nacional |

## 🚀 Como Usar

### Via HTTP
```html
<!-- Exemplo de uso na interface -->
<img src="/assets/flags/SP.svg" alt="São Paulo" class="flag-icon">
```

### Via Docker
```bash
# Acessar via nginx
http://localhost:8787/assets/flags/SP.svg
```

## 🔧 Geração das Bandeiras

### Script de Geração
```bash
# Executar script para gerar/atualizar bandeiras
./download_flags.sh
```

### Processo
1. **Tentativa de download** de bandeiras reais
2. **Fallback automático** para bandeiras simplificadas
3. **Geração SVG** com cores específicas
4. **Salvamento** na pasta `assets/flags/`

## 📊 Estatísticas

- **Total de bandeiras**: 27
- **Formato**: SVG
- **Tamanho médio**: ~331 bytes por arquivo
- **Tamanho total**: ~9KB

## 🎨 Personalização

### Cores
As cores das bandeiras podem ser personalizadas editando o script `download_flags.sh`:

```bash
# Exemplo de personalização de cores
case $state in
    "SP") color1="#ffffff"; color2="#000000" ;;  # SP: branco e preto
    "RJ") color1="#ffffff"; color2="#0000ff" ;;  # RJ: branco e azul
    # ... outras personalizações
esac
```

### Dimensões
As dimensões podem ser alteradas no SVG:
```xml
<svg viewBox="0 0 24 16" width="24" height="16">
```

## 🔄 Atualização

### Adicionar Novo Estado
1. Adicionar entrada no array `flags` no script
2. Executar `./download_flags.sh`
3. Atualizar array `estados` no `index.html`

### Modificar Bandeira Existente
1. Editar cores no script `download_flags.sh`
2. Executar script novamente
3. Reiniciar containers: `docker-compose restart`

## 📝 Notas

- **Cache**: Bandeiras são cacheadas por 1 ano no navegador
- **CORS**: Headers configurados para permitir acesso cross-origin
- **Fallback**: Sistema robusto com fallback para bandeiras simplificadas
- **Performance**: SVG otimizado para carregamento rápido

## 🐛 Troubleshooting

### Bandeira não carrega
1. Verificar se arquivo existe: `ls assets/flags/ESTADO.svg`
2. Verificar permissões: `chmod 644 assets/flags/*.svg`
3. Verificar nginx: `docker-compose logs nginx`

### Bandeira com cores erradas
1. Editar script `download_flags.sh`
2. Executar script novamente
3. Reiniciar containers

### Performance lenta
1. Verificar cache do navegador
2. Verificar headers de cache no nginx
3. Otimizar SVGs se necessário 