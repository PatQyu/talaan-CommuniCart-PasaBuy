const login_tab = document.getElementById('login-tab');
const register_tab = document.getElementById('register-tab');

const login_form = document.getElementById('login-form');
const register_form = document.getElementById('register-form');

const login_sc = document.getElementById('login_sc');
const register_sc = document.getElementById('register_sc');

login_tab.addEventListener('click', () => {
    login_tab.classList.add('tab_is_active');
    register_tab.classList.remove('tab_is_active');
    login_form.classList.remove('is-hidden');
    register_form.classList.add('is-hidden');
});

register_tab.addEventListener('click', () => {
    register_tab.classList.add('tab_is_active');
    login_tab.classList.remove('tab_is_active');
    register_form.classList.remove('is-hidden');
    login_form.classList.add('is-hidden');
});