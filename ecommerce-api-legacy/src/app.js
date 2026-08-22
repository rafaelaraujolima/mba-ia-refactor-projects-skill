const express = require('express');
const bcrypt = require('bcrypt');
const settings = require('./config/settings');
const { connectDb } = require('./config/db');
const { errorHandler } = require('./middlewares/errorHandler');
const logger = require('./utils/logger');
const buildRoutes = require('./routes');

const userModel = require('./models/userModel');
const courseModel = require('./models/courseModel');
const enrollmentModel = require('./models/enrollmentModel');
const paymentModel = require('./models/paymentModel');
const auditLogModel = require('./models/auditLogModel');

const authController = require('./controllers/authController');
const checkoutController = require('./controllers/checkoutController');
const reportController = require('./controllers/reportController');
const userController = require('./controllers/userController');

const SEED_PASSWORD = '123';
const SALT_ROUNDS = 10;

async function main() {
    const hashedSeedPassword = await bcrypt.hash(SEED_PASSWORD, SALT_ROUNDS);
    const db = await connectDb(hashedSeedPassword);

    const models = {
        userModel: userModel(db),
        courseModel: courseModel(db),
        enrollmentModel: enrollmentModel(db),
        paymentModel: paymentModel(db),
        auditLogModel: auditLogModel(db),
    };

    const controllers = {
        authController: authController(models),
        checkoutController: checkoutController(models),
        reportController: reportController(models),
        userController: userController(models),
    };

    const app = express();
    app.use(express.json());
    app.use(buildRoutes(controllers));
    app.use(errorHandler);

    app.listen(settings.port, () => {
        logger.info(`LMS API rodando na porta ${settings.port}`);
    });
}

main().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
