const login_tab = document.getElementById('login-tab');
const register_tab = document.getElementById('register-tab');

const login_form = document.getElementById('login-form');
const register_form = document.getElementById('register-form');

const login_sc = document.getElementById('login-sc');
const register_sc = document.getElementById('register-sc');

function showMessage(formElement, message, isError = false) {
    let statusEl = formElement.querySelector('.auth-status');
    if (!statusEl) {
        statusEl = document.createElement('p');
        statusEl.className = 'auth-footnote auth-status';
        formElement.appendChild(statusEl);
    }

    statusEl.textContent = message;
    statusEl.style.color = isError ? '#cc2f3c' : '';
}

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

login_form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            throw new Error(data.message || 'Login failed.');
        }

        localStorage.setItem('user_id', String(data.user_id));
        showMessage(login_form, 'Login successful. Redirecting to app output...');
        window.location.href = '/app-output';
    } catch (error) {
        showMessage(login_form, error.message, true);
    }
});

register_form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
        username: document.getElementById('new-username').value.trim(),
        email: document.getElementById('new-email').value.trim(),
        password: document.getElementById('new-password').value
    };

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            throw new Error(data.message || 'Sign up failed.');
        }

        showMessage(register_form, 'Account created. You can login now.');
        showLoginForm();
    } catch (error) {
        showMessage(register_form, error.message, true);
    }
});