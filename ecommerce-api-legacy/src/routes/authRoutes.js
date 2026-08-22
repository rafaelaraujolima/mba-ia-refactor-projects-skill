const express = require('express');

function authRoutes({ authController }) {
    const router = express.Router();

    router.post('/api/login', async (req, res, next) => {
        try {
            const result = await authController.login(req.body);
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = authRoutes;
