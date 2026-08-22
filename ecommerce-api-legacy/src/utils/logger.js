const settings = require('../config/settings');

const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };
const currentLevel = LEVELS[settings.logLevel] ?? LEVELS.info;

function log(level, message, meta) {
    if (LEVELS[level] > currentLevel) return;
    const line = `[${new Date().toISOString()}] [${level.toUpperCase()}] ${message}`;
    if (meta !== undefined) {
        console.log(line, meta);
    } else {
        console.log(line);
    }
}

module.exports = {
    error: (message, meta) => log('error', message, meta),
    warn: (message, meta) => log('warn', message, meta),
    info: (message, meta) => log('info', message, meta),
    debug: (message, meta) => log('debug', message, meta),
};
