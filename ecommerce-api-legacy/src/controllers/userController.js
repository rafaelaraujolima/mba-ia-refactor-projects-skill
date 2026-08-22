const { AppError } = require('../middlewares/errorHandler');

function userController({ userModel, enrollmentModel, paymentModel }) {
    return {
        async deleteUser({ requestingUser, targetId }) {
            const isSelf = requestingUser.sub === Number(targetId);
            if (!isSelf && !requestingUser.isAdmin) {
                throw new AppError('Acesso negado', 403);
            }

            const target = await userModel.findById(targetId);
            if (!target) {
                throw new AppError('Usuário não encontrado', 404);
            }

            const enrollments = await enrollmentModel.findByUserId(targetId);
            const enrollmentIds = enrollments.map((e) => e.id);

            await paymentModel.deleteByEnrollmentIds(enrollmentIds);
            await enrollmentModel.deleteByIds(enrollmentIds);
            await userModel.deleteById(targetId);

            return { msg: 'Usuário e dados relacionados removidos com sucesso' };
        },
    };
}

module.exports = userController;
