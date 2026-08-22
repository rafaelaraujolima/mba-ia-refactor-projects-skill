const bcrypt = require('bcrypt');
const { AppError } = require('../middlewares/errorHandler');
const logger = require('../utils/logger');

const SALT_ROUNDS = 10;
const DEFAULT_PASSWORD = '123456';
const APPROVED_CARD_PREFIX = '4';

function checkoutController({ courseModel, userModel, enrollmentModel, paymentModel, auditLogModel }) {
    return {
        async checkout({ username, email, password, courseId, cardNumber }) {
            if (!username || !email || !courseId || !cardNumber) {
                throw new AppError('Campos obrigatórios ausentes', 400);
            }

            const course = await courseModel.findActiveById(courseId);
            if (!course) {
                throw new AppError('Curso não encontrado', 404);
            }

            let user = await userModel.findByEmail(email);
            if (!user) {
                const passwordHash = await bcrypt.hash(password || DEFAULT_PASSWORD, SALT_ROUNDS);
                user = await userModel.create({ name: username, email, passwordHash });
            }

            logger.info(`Processando pagamento do curso ${courseId} para o usuário ${user.id}`);
            const status = cardNumber.startsWith(APPROVED_CARD_PREFIX) ? 'PAID' : 'DENIED';
            if (status === 'DENIED') {
                throw new AppError('Pagamento recusado', 400);
            }

            const enrollment = await enrollmentModel.create(user.id, courseId);
            await paymentModel.create(enrollment.id, course.price, status);
            await auditLogModel.create(`Checkout curso ${courseId} por ${user.id}`);

            return { msg: 'Sucesso', enrollment_id: enrollment.id };
        },
    };
}

module.exports = checkoutController;
