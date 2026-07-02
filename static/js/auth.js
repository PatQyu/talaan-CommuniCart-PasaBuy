const login_tab = document.getElementById('login-tab');
const register_tab = document.getElementById('register-tab');

const login_form = document.getElementById('login-form');
const register_form = document.getElementById('register-form');

const login_sc = document.getElementById('login-sc');
const register_sc = document.getElementById('register-sc');

function showLoginForm(e) {
    if (e) e.preventDefault(); 
    login_tab.classList.add('tab_is_active');     
    register_tab.classList.remove('tab_is_active'); 
    login_form.classList.remove('is-hidden');
    register_form.classList.add('is-hidden');
}

function showRegisterForm(e) {
    if (e) e.preventDefault(); 
    register_tab.classList.add('tab_is_active');   
    login_tab.classList.remove('tab_is_active');  
    register_form.classList.remove('is-hidden');
    login_form.classList.add('is-hidden');
}

login_tab.addEventListener('click', showLoginForm);  
register_tab.addEventListener('click', showRegisterForm);

login_sc.addEventListener('click', showLoginForm);
register_sc.addEventListener('click', showRegisterForm);

login_form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });
        
        const data = await response.json();

        if (response.ok && data.status === 'success') {
            localStorage.setItem('user_id', data.user_id);
            alert("Login success");
            
            window.location.href = '/calculator'; 
        } else {
            alert(data.message || "Invalid email or password.");
        }
    } catch (error) {
        console.error("Login Error:", error);
        alert("Cannot connect to the server.");
    }
});

register_form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('new-username').value;
    const email = document.getElementById('new-email').value;
    const password = document.getElementById('new-password').value;

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, email: email, password: password })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            alert("Account created");
            register_form.reset();
            showLoginForm();
        } else {
            alert(data.message || "Error creating account.");
        }
    } catch (error) {
        console.error("Signup Error:", error);
        alert("Cannot connect to the server.");
    }
});