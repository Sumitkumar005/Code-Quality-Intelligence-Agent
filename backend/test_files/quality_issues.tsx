// Test file with code quality issues for CLI testing

import React, { useState, useEffect } from 'react';

// CODE QUALITY ISSUE: No TypeScript types
function UserProfile(props) {
    const [user, setUser] = useState();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState();

    // CODE QUALITY ISSUE: Missing dependency array
    useEffect(() => {
        fetchUserData();
    });

    // CODE QUALITY ISSUE: No error handling
    const fetchUserData = async () => {
        setLoading(true);
        const response = await fetch(`/api/users/${props.userId}`);
        const userData = await response.json();
        setUser(userData);
        setLoading(false);
    };

    // CODE QUALITY ISSUE: Complex nested conditionals
    const renderUserInfo = () => {
        if (user) {
            if (user.profile) {
                if (user.profile.personal) {
                    if (user.profile.personal.name) {
                        if (user.profile.personal.name.first && user.profile.personal.name.last) {
                            return (
                                <div>
                                    <h1>{user.profile.personal.name.first} {user.profile.personal.name.last}</h1>
                                    {user.profile.personal.email && (
                                        <p>{user.profile.personal.email}</p>
                                    )}
                                    {user.profile.personal.phone && (
                                        <p>{user.profile.personal.phone}</p>
                                    )}
                                </div>
                            );
                        }
                    }
                }
            }
        }
        return <div>No user data available</div>;
    };

    // CODE QUALITY ISSUE: Duplicate code
    const handleSave = () => {
        if (!user) return;
        if (!user.profile) return;
        if (!user.profile.personal) return;
        
        const data = {
            name: user.profile.personal.name,
            email: user.profile.personal.email,
            phone: user.profile.personal.phone
        };
        
        fetch('/api/users/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    };

    const handleUpdate = () => {
        if (!user) return;
        if (!user.profile) return;
        if (!user.profile.personal) return;
        
        const data = {
            name: user.profile.personal.name,
            email: user.profile.personal.email,
            phone: user.profile.personal.phone
        };
        
        fetch('/api/users/update', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    };

    // CODE QUALITY ISSUE: Magic numbers and hardcoded values
    const processUserData = (userData) => {
        const score = userData.activities.length * 10 + userData.friends.length * 5;
        if (score > 100) {
            userData.level = 'premium';
        } else if (score > 50) {
            userData.level = 'standard';
        } else {
            userData.level = 'basic';
        }
        
        // More magic numbers
        userData.maxConnections = userData.level === 'premium' ? 1000 : 
                                 userData.level === 'standard' ? 500 : 100;
        
        return userData;
    };

    // CODE QUALITY ISSUE: Long parameter list
    const createUserReport = (userId, userName, userEmail, userPhone, userAddress, 
                            userCity, userState, userZip, userCountry, userAge, 
                            userGender, userOccupation, userIncome, userEducation) => {
        return {
            id: userId,
            name: userName,
            contact: {
                email: userEmail,
                phone: userPhone,
                address: {
                    street: userAddress,
                    city: userCity,
                    state: userState,
                    zip: userZip,
                    country: userCountry
                }
            },
            demographics: {
                age: userAge,
                gender: userGender,
                occupation: userOccupation,
                income: userIncome,
                education: userEducation
            }
        };
    };

    // CODE QUALITY ISSUE: Inconsistent naming and formatting
    const handle_click = (e) => {
        const UserID = e.target.dataset.userid;
        const user_name = e.target.dataset.username;
        
        if(UserID&&user_name){
            setUser({...user,selectedUser:UserID,selectedName:user_name});
        }
    };

    return (
        <div>
            {loading && <div>Loading...</div>}
            {error && <div>Error: {error}</div>}
            {renderUserInfo()}
            <button onClick={handleSave}>Save</button>
            <button onClick={handleUpdate}>Update</button>
        </div>
    );
}

// CODE QUALITY ISSUE: No default export, inconsistent exports
export { UserProfile };

// CODE QUALITY ISSUE: Unused variables and imports
const unusedVariable = 'this is never used';
const anotherUnusedVar = 42;