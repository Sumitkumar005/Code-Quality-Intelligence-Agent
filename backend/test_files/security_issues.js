// Test file with security issues for CLI testing

const express = require('express');
const mysql = require('mysql');
const app = express();

// SECURITY ISSUE: Hardcoded credentials
const password = "admin123";
const api_key = "sk-1234567890abcdef";
const secret_token = "my_secret_token_123";

// SECURITY ISSUE: SQL Injection vulnerability
function getUserById(userId) {
    const query = "SELECT * FROM users WHERE id = " + userId;
    return db.query(query);
}

// SECURITY ISSUE: Unsafe eval usage
function processUserInput(input) {
    return eval(input);
}

// SECURITY ISSUE: XSS vulnerability
function displayMessage(message) {
    document.getElementById('output').innerHTML = message;
}

// PERFORMANCE ISSUE: Inefficient loop
function processLargeArray(items) {
    let result = [];
    for (let i = 0; i < items.length; i++) {
        for (let j = 0; j < items.length; j++) {
            if (items[i].id === items[j].parentId) {
                result.push(items[i]);
            }
        }
    }
    return result;
}

// CODE QUALITY ISSUE: Long function with high complexity
function complexBusinessLogic(user, order, payment, shipping, discount, tax) {
    if (user && user.isActive) {
        if (order && order.items && order.items.length > 0) {
            if (payment && payment.method) {
                if (payment.method === 'credit_card') {
                    if (payment.card && payment.card.number) {
                        if (shipping && shipping.address) {
                            if (discount && discount.code) {
                                if (discount.isValid) {
                                    if (tax && tax.rate) {
                                        // Deep nesting continues...
                                        let total = 0;
                                        for (let item of order.items) {
                                            total += item.price * item.quantity;
                                        }
                                        total = total * (1 - discount.rate);
                                        total = total * (1 + tax.rate);
                                        return total;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return 0;
}

module.exports = { getUserById, processUserInput, displayMessage, processLargeArray, complexBusinessLogic };