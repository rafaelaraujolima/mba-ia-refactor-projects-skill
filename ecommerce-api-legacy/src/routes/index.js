const express = require('express');
const authRoutes = require('./authRoutes');
const checkoutRoutes = require('./checkoutRoutes');
const reportRoutes = require('./reportRoutes');
const userRoutes = require('./userRoutes');

function buildRoutes(controllers) {
    const router = express.Router();

    router.use(authRoutes(controllers));
    router.use(checkoutRoutes(controllers));
    router.use(reportRoutes(controllers));
    router.use(userRoutes(controllers));

    return router;
}

module.exports = buildRoutes;
