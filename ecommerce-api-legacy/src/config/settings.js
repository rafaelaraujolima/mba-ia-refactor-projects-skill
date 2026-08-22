require('dotenv').config();

function required(name) {
    const value = process.env[name];
    if (!value) {
        throw new Error(`${name} environment variable is required`);
    }
    return value;
}

const settings = {
    port: parseInt(process.env.PORT, 10) || 3000,
    dbUser: required('DB_USER'),
    dbPass: required('DB_PASS'),
    paymentGatewayKey: required('PAYMENT_GATEWAY_KEY'),
    smtpUser: required('SMTP_USER'),
    jwtSecret: required('JWT_SECRET'),
    logLevel: process.env.LOG_LEVEL || 'info',
};

module.exports = settings;
