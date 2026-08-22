const express = require('express');

function checkoutRoutes({ checkoutController }) {
    const router = express.Router();

    router.post('/api/checkout', async (req, res, next) => {
        try {
            const result = await checkoutController.checkout({
                username: req.body.usr,
                email: req.body.eml,
                password: req.body.pwd,
                courseId: req.body.c_id,
                cardNumber: req.body.card,
            });
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = checkoutRoutes;
