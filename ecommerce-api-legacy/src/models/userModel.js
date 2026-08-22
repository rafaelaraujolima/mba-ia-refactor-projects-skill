function placeholders(list) {
    return list.map(() => '?').join(',');
}

function userModel(db) {
    return {
        async findByEmail(email) {
            return db.get('SELECT * FROM users WHERE email = ?', [email]);
        },

        async findByIds(ids) {
            if (ids.length === 0) return [];
            return db.all(`SELECT * FROM users WHERE id IN (${placeholders(ids)})`, ids);
        },

        async findById(id) {
            return db.get('SELECT * FROM users WHERE id = ?', [id]);
        },

        async create({ name, email, passwordHash, isAdmin = 0 }) {
            const { lastID } = await db.run(
                'INSERT INTO users (name, email, pass, is_admin) VALUES (?, ?, ?, ?)',
                [name, email, passwordHash, isAdmin ? 1 : 0]
            );
            return this.findById(lastID);
        },

        async deleteById(id) {
            const { changes } = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return changes > 0;
        },
    };
}

module.exports = userModel;
