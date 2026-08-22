function placeholders(list) {
    return list.map(() => '?').join(',');
}

function paymentModel(db) {
    return {
        async create(enrollmentId, amount, status) {
            const { lastID } = await db.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amount, status]
            );
            return db.get('SELECT * FROM payments WHERE id = ?', [lastID]);
        },

        async findByEnrollmentIds(enrollmentIds) {
            if (enrollmentIds.length === 0) return [];
            return db.all(
                `SELECT * FROM payments WHERE enrollment_id IN (${placeholders(enrollmentIds)})`,
                enrollmentIds
            );
        },

        async deleteByEnrollmentIds(enrollmentIds) {
            if (enrollmentIds.length === 0) return;
            await db.run(
                `DELETE FROM payments WHERE enrollment_id IN (${placeholders(enrollmentIds)})`,
                enrollmentIds
            );
        },
    };
}

module.exports = paymentModel;
