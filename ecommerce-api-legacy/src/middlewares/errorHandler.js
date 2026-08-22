const logger = require('../utils/logger');

class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

function errorHandler(err, req, res, next) { // eslint-disable-line no-unused-vars
    if (err instanceof AppError) {
        return res.status(err.statusCode).json({ error: err.message });
    }
    logger.error('Unhandled error', err);
    return res.status(500).json({ error: 'Internal server error' });
}

module.exports = { AppError, errorHandler };
