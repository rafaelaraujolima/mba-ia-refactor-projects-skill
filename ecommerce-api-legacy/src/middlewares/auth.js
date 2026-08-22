const jwt = require('jsonwebtoken');
const settings = require('../config/settings');
const { AppError } = require('./errorHandler');

function requireAuth({ adminOnly = false } = {}) {
    return (req, res, next) => {
        const header = req.headers.authorization || '';
        const token = header.startsWith('Bearer ') ? header.slice('Bearer '.length) : null;

        if (!token) {
            return next(new AppError('Não autorizado', 401));
        }

        try {
            const payload = jwt.verify(token, settings.jwtSecret);
            if (adminOnly && !payload.isAdmin) {
                return next(new AppError('Acesso negado', 403));
            }
            req.user = payload;
            return next();
        } catch (err) {
            return next(new AppError('Token inválido', 401));
        }
    };
}

module.exports = { requireAuth };
