function courseModel(db) {
    return {
        async findActiveById(id) {
            return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
        },

        async findAll() {
            return db.all('SELECT * FROM courses', []);
        },
    };
}

module.exports = courseModel;
