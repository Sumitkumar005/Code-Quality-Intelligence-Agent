// Utility functions with various code quality issues

// CODE QUALITY ISSUE: No TypeScript types
export function formatDate(date) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // CODE QUALITY ISSUE: No null/undefined checks
    const month = months[date.getMonth()];
    const day = date.getDate();
    const year = date.getFullYear();

    return `${month} ${day}, ${year}`;
}

// CODE QUALITY ISSUE: Function too long and complex
export function processUserData(userData, options, settings, preferences, config) {
    let result = {};

    if (userData && userData.profile) {
        if (options && options.includePersonal) {
            if (userData.profile.personal) {
                result.name = userData.profile.personal.firstName + ' ' + userData.profile.personal.lastName;
                result.email = userData.profile.personal.email;
                result.phone = userData.profile.personal.phone;

                if (settings && settings.formatPhone) {
                    if (result.phone && result.phone.length === 10) {
                        result.phone = `(${result.phone.slice(0, 3)}) ${result.phone.slice(3, 6)}-${result.phone.slice(6)}`;
                    }
                }

                if (preferences && preferences.showAge) {
                    if (userData.profile.personal.birthDate) {
                        const today = new Date();
                        const birthDate = new Date(userData.profile.personal.birthDate);
                        let age = today.getFullYear() - birthDate.getFullYear();
                        const monthDiff = today.getMonth() - birthDate.getMonth();

                        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                            age--;
                        }

                        result.age = age;
                    }
                }
            }
        }

        if (options && options.includeWork) {
            if (userData.profile.work) {
                result.company = userData.profile.work.company;
                result.position = userData.profile.work.position;
                result.salary = userData.profile.work.salary;

                if (config && config.hideSalary) {
                    delete result.salary;
                }

                if (userData.profile.work.startDate) {
                    const startDate = new Date(userData.profile.work.startDate);
                    const today = new Date();
                    const diffTime = Math.abs(today - startDate);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    const years = Math.floor(diffDays / 365);
                    const months = Math.floor((diffDays % 365) / 30);

                    result.experience = `${years} years, ${months} months`;
                }
            }
        }
    }

    return result;
}

// CODE QUALITY ISSUE: Magic numbers and unclear logic
export function calculateScore(metrics) {
    let score = 0;

    score += metrics.commits * 2.5;
    score += metrics.pullRequests * 15;
    score += metrics.codeReviews * 8;
    score += metrics.issuesResolved * 12;

    if (metrics.testCoverage > 80) {
        score *= 1.2;
    } else if (metrics.testCoverage > 60) {
        score *= 1.1;
    } else if (metrics.testCoverage < 40) {
        score *= 0.8;
    }

    if (metrics.bugCount > 10) {
        score *= 0.7;
    } else if (metrics.bugCount > 5) {
        score *= 0.9;
    }

    return Math.round(score);
}

// CODE QUALITY ISSUE: Inconsistent naming and poor structure
export const user_utils = {
    get_full_name: function (user) {
        return user.firstName + " " + user.lastName;
    },

    getUserAge: (user) => {
        const today = new Date();
        const birthDate = new Date(user.birthDate);
        return today.getFullYear() - birthDate.getFullYear();
    },

    format_email: function (email) {
        return email.toLowerCase().trim();
    }
};

// CODE QUALITY ISSUE: Duplicate code
export function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

export function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// PERFORMANCE ISSUE: Inefficient array operations
export function findDuplicates(array) {
    const duplicates = [];

    for (let i = 0; i < array.length; i++) {
        for (let j = i + 1; j < array.length; j++) {
            if (array[i] === array[j] && !duplicates.includes(array[i])) {
                duplicates.push(array[i]);
            }
        }
    }

    return duplicates;
}