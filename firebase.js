// Fetch user data from JSON file
async function fetchUsers() {
    const response = await fetch('users.json');
    return await response.json();
}

// Sign In Function
document.getElementById('signInForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const email = this.querySelector('input[type="email"]').value;
    const password = this.querySelector('input[type="password"]').value;
    const userRole = document.getElementById('userRole').value;

    const users = await fetchUsers();
    const user = users.find(user => user.email === email && user.password === password && user.role === userRole);
    
    if (user) {
        // Redirect based on user role
        if (userRole === 'customer') {
            window.location.href = 'customer_dashboard.html';
        } else if (userRole === 'restaurant') {
            window.location.href = 'restaurant_dashboard.html';
        } else if (userRole === 'admin') {
            window.location.href = 'admin_dashboard.html';
        }
    } else {
        alert("Invalid credentials. Please try again.");
    }
});
