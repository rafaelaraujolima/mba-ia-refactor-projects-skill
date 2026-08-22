function auditLogModel(db) {
    return {
        async create(action) {
            await db.run(
                "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
                [action]
            );
        },
    };
}

module.exports = auditLogModel;
