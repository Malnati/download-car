#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Função para ler variáveis de ambiente
function getEnvVar(name, defaultValue = '') {
    return process.env[name] || defaultValue;
}

// Função para gerar objeto STATE_TIMEOUTS
function generateStateTimeouts() {
    const states = [
        'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN',
        'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
    ];
    
    const timeouts = {};
    states.forEach(state => {
        const timeout = getEnvVar(`STATE_TIMEOUT_${state}`, '60000');
        timeouts[state] = parseInt(timeout);
    });
    
    return timeouts;
}

// Função para gerar configuração JavaScript
function generateConfig() {
    const config = {
        API_ENDPOINT_URL: getEnvVar('API_ENDPOINT_URL', 'http://192.168.5.179:8787'),
        DEFAULT_TIMEOUT: parseInt(getEnvVar('DEFAULT_TIMEOUT', '800000')),
        TIMEOUT_INCREMENT: parseInt(getEnvVar('TIMEOUT_INCREMENT', '10000')),
        MIN_TIMEOUT: parseInt(getEnvVar('MIN_TIMEOUT', '10000')),
        MAX_TIMEOUT: parseInt(getEnvVar('MAX_TIMEOUT', '300000')),
        DEFAULT_POLYGON: getEnvVar('DEFAULT_POLYGON', 'AREA_PROPERTY'),
        STATE_TIMEOUTS: generateStateTimeouts()
    };
    
    return config;
}

// Função para substituir configuração no index.html
function updateIndexHtml() {
    const indexPath = path.join(__dirname, '..', 'index.html');
    const templatePath = path.join(__dirname, 'index.html.template');
    
    // Se não existir template, usar o index.html atual
    const sourcePath = fs.existsSync(templatePath) ? templatePath : indexPath;
    
    let content = fs.readFileSync(sourcePath, 'utf8');
    const config = generateConfig();
    
    // Substituir configurações
    content = content.replace(
        /const DEFAULT_API_URL = '[^']*';/,
        `const DEFAULT_API_URL = '${config.API_ENDPOINT_URL}';`
    );
    
    content = content.replace(
        /const DEFAULT_TIMEOUT = \d+;/,
        `const DEFAULT_TIMEOUT = ${config.DEFAULT_TIMEOUT};`
    );
    
    content = content.replace(
        /const TIMEOUT_INCREMENT = \d+;/,
        `const TIMEOUT_INCREMENT = ${config.TIMEOUT_INCREMENT};`
    );
    
    content = content.replace(
        /const MIN_TIMEOUT = \d+;/,
        `const MIN_TIMEOUT = ${config.MIN_TIMEOUT};`
    );
    
    content = content.replace(
        /const MAX_TIMEOUT = \d+;/,
        `const MAX_TIMEOUT = ${config.MAX_TIMEOUT};`
    );
    
    content = content.replace(
        /const DEFAULT_POLYGON = '[^']*';/,
        `const DEFAULT_POLYGON = '${config.DEFAULT_POLYGON}';`
    );
    
    // Substituir STATE_TIMEOUTS
    const stateTimeoutsStr = JSON.stringify(config.STATE_TIMEOUTS, null, 12)
        .replace(/"([^"]+)":/g, "'$1':")
        .replace(/"/g, '')
        .split('\n')
        .map(line => '            ' + line)
        .join('\n');
    
    const stateTimeoutsRegex = /const STATE_TIMEOUTS = \{[\s\S]*?\};/;
    content = content.replace(stateTimeoutsRegex, `const STATE_TIMEOUTS = {\n${stateTimeoutsStr}\n        };`);
    
    // Escrever arquivo atualizado
    fs.writeFileSync(indexPath, content, 'utf8');
    
    console.log('Configuração do frontend atualizada com variáveis de ambiente');
    console.log('Configuração gerada:', JSON.stringify(config, null, 2));
}

// Executar se chamado diretamente
if (require.main === module) {
    updateIndexHtml();
}

module.exports = { generateConfig, updateIndexHtml }; 