const express = require('express');
const { requireAuth } = require('../middlewares/auth');

function userRoutes({ userController }) {
    const router = express.Router();

    router.delete('/api/users/:id', requireAuth(), async (req, res, next) => {
        try {
            const result = await userController.deleteUser({
                requestingUser: req.user,
                targetId: req.params.id,
            });
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = userRoutes;
