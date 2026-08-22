const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const settings = require('../config/settings');
const { AppError } = require('../middlewares/errorHandler');

function authController({ userModel }) {
    return {
        async login({ email, password }) {
            if (!email || !password) {
                throw new AppError('E-mail e senha são obrigatórios', 400);
            }

            const user = await userModel.findByEmail(email);
            if (!user || !(await bcrypt.compare(password, user.pass))) {
                throw new AppError('Credenciais inválidas', 401);
            }

            const token = jwt.sign(
                { sub: user.id, isAdmin: !!user.is_admin },
                settings.jwtSecret,
                { expiresIn: '2h' }
            );

            return { token };
        },
    };
}

module.exports = authController;
