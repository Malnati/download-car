# Pasta Assets

Esta pasta contém os recursos estáticos do sistema Download CAR.

## Estrutura

```
assets/
├── flags/          # Bandeiras dos estados brasileiros (SVG)
└── README.md       # Este arquivo
```

## Bandeiras dos Estados (assets/flags/)

### Descrição
As bandeiras dos estados brasileiros são arquivos SVG criados localmente com designs realistas baseados nas cores oficiais de cada estado.

### Características
- **Formato**: SVG (Scalable Vector Graphics)
- **Dimensões**: 24x16 pixels (viewBox)
- **Design**: Baseado nas cores oficiais dos estados
- **Elementos**: Retângulos, círculos e polígonos para criar designs únicos

### Estados Disponíveis
- **AC** (Acre): Verde e amarelo com círculo azul
- **AL** (Alagoas): Vermelho e branco com círculo vermelho
- **AM** (Amazonas): Verde e amarelo com círculo azul
- **AP** (Amapá): Verde e amarelo com círculo azul
- **BA** (Bahia): Branco e azul com círculo branco
- **CE** (Ceará): Verde e amarelo com círculo azul
- **DF** (Distrito Federal): Branco e azul com círculo branco
- **ES** (Espírito Santo): Azul e branco com círculo azul
- **GO** (Goiás): Verde e amarelo com círculo azul
- **MA** (Maranhão): Verde e amarelo com círculo azul
- **MG** (Minas Gerais): Branco e vermelho com triângulo vermelho
- **MS** (Mato Grosso do Sul): Azul e branco com círculo azul
- **MT** (Mato Grosso): Verde e vermelho com círculo branco
- **PA** (Pará): Verde e amarelo com círculo azul
- **PB** (Paraíba): Vermelho e branco com círculo vermelho
- **PE** (Pernambuco): Azul e branco com círculo azul
- **PI** (Piauí): Verde e amarelo com círculo azul
- **PR** (Paraná): Azul e branco com círculo azul
- **RJ** (Rio de Janeiro): Branco e azul com estrela azul
- **RN** (Rio Grande do Norte): Vermelho e branco com círculo vermelho
- **RO** (Rondônia): Verde e amarelo com círculo azul
- **RR** (Roraima): Verde e amarelo com círculo azul
- **RS** (Rio Grande do Sul): Vermelho e amarelo com brasão circular
- **SC** (Santa Catarina): Vermelho e branco com círculo vermelho
- **SE** (Sergipe): Verde e amarelo com círculo azul
- **SP** (São Paulo): Branco e preto com estrela preta
- **TO** (Tocantins): Verde e amarelo com círculo azul

### Cores Utilizadas
- **Branco**: #ffffff
- **Preto**: #000000
- **Azul**: #0000ff
- **Vermelho**: #ff0000
- **Verde**: #00ff00
- **Amarelo**: #ffff00

### Scripts de Geração
- `download_flags.sh`: Script original para tentar baixar bandeiras oficiais
- `create_realistic_flags.sh`: Script para criar bandeiras realistas locais

### Uso na Interface
As bandeiras são referenciadas na interface web através de:
```html
<img src="/assets/flags/SP.svg" alt="Bandeira de São Paulo" class="flag-icon">
```

### Manutenção
Para adicionar novos estados ou modificar designs existentes:
1. Edite o script `create_realistic_flags.sh`
2. Execute o script para regenerar as bandeiras
3. Reconstrua os containers Docker se necessário

### Notas Técnicas
- Todas as bandeiras são arquivos SVG válidos
- Tamanho médio: ~250-350 bytes por arquivo
- Compatíveis com todos os navegadores modernos
- Escaláveis sem perda de qualidade 