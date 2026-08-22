function placeholders(list) {
    return list.map(() => '?').join(',');
}

function enrollmentModel(db) {
    return {
        async create(userId, courseId) {
            const { lastID } = await db.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, courseId]
            );
            return this.findById(lastID);
        },

        async findById(id) {
            return db.get('SELECT * FROM enrollments WHERE id = ?', [id]);
        },

        async findByCourseIds(courseIds) {
            if (courseIds.length === 0) return [];
            return db.all(
                `SELECT * FROM enrollments WHERE course_id IN (${placeholders(courseIds)})`,
                courseIds
            );
        },

        async findByUserId(userId) {
            return db.all('SELECT * FROM enrollments WHERE user_id = ?', [userId]);
        },

        async deleteByIds(ids) {
            if (ids.length === 0) return;
            await db.run(`DELETE FROM enrollments WHERE id IN (${placeholders(ids)})`, ids);
        },
    };
}

module.exports = enrollmentModel;
