const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');
const logger = require('../utils/logger');

function createConnection() {
    return new sqlite3.Database(':memory:');
}

function wrapConnection(db) {
    const get = promisify(db.get.bind(db));
    const all = promisify(db.all.bind(db));

    function run(sql, params = []) {
        return new Promise((resolve, reject) => {
            db.run(sql, params, function onRun(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    return { get, all, run, raw: db };
}

async function initSchema(db) {
    await db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT, is_admin INTEGER DEFAULT 0)');
    await db.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await db.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await db.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await db.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seed(db, hashedSeedPassword) {
    const user = await db.run(
        'INSERT INTO users (name, email, pass, is_admin) VALUES (?, ?, ?, 1)',
        ['Leonan', 'leonan@fullcycle.com.br', hashedSeedPassword]
    );
    const course1 = await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, 1)',
        ['Clean Architecture', 997.0]
    );
    await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1)', ['Docker', 497.0]);
    const enrollment = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [user.lastID, course1.lastID]
    );
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollment.lastID, 997.0, 'PAID']
    );
}

async function connectDb(hashedSeedPassword) {
    const db = wrapConnection(createConnection());
    await initSchema(db);
    await seed(db, hashedSeedPassword);
    logger.info('Database connected and seeded (in-memory)');
    return db;
}

module.exports = { connectDb };
