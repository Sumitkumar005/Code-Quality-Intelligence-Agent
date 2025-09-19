// Authentication module with various issues

const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

// SECURITY ISSUE: Hardcoded JWT secret
const JWT_SECRET = "my-super-secret-key-123";

// SECURITY ISSUE: Weak password validation
function validatePassword(password) {
    return password.length >= 6; // Too weak
}

// SECURITY ISSUE: No rate limiting
function login(username, password) {
    const user = getUserFromDB(username);
    
    if (user && bcrypt.compareSync(password, user.hashedPassword)) {
        // SECURITY ISSUE: No expiration time
        const token = jwt.sign({ userId: user.id }, JWT_SECRET);
        return { success: true, token };
    }
    
    return { success: false, message: "Invalid credentials" };
}

// PERFORMANCE ISSUE: Synchronous database operation
function getUserFromDB(username) {
    // Simulated slow database operation
    const users = getAllUsers(); // Loads all users instead of querying one
    return users.find(u => u.username === username);
}

function getAllUsers() {
    // Simulated large dataset
    const users = [];
    for (let i = 0; i < 10000; i++) {
        users.push({
            id: i,
            username: `user${i}`,
            hashedPassword: `hash${i}`
        });
    }
    return users;
}

module.exports = { login, validatePassword };