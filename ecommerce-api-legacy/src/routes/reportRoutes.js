const express = require('express');
const { requireAuth } = require('../middlewares/auth');

function reportRoutes({ reportController }) {
    const router = express.Router();

    router.get('/api/admin/financial-report', requireAuth({ adminOnly: true }), async (req, res, next) => {
        try {
            const report = await reportController.buildFinancialReport();
            res.status(200).json(report);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = reportRoutes;
