// Seleciona o formulário de login dentro do cabeçalho
let loginForm = document.querySelector('.header .login-form');

// Quando o ícone de usuário (login) for clicado:
document.querySelector('#login-btn').onclick = () => {
    // Alterna a visibilidade do formulário de login (mostra/esconde)
    loginForm.classList.toggle('active');

    // Garante que o menu de navegação será fechado, caso esteja aberto
    navbar.classList.remove('active');
};

// Seleciona o menu de navegação dentro do cabeçalho
let navbar = document.querySelector('.header .navbar');

// Quando o ícone de menu (☰) for clicado:
document.querySelector('#menu-btn').onclick = () => {
    // Alterna a visibilidade do menu de navegação (mostra/esconde)
    navbar.classList.toggle('active');

    // Garante que o formulário de login será fechado, caso esteja aberto
    loginForm.classList.remove('active');
};


window.onload = () => {
    if (window.scrollY > 0) {
    // Remove a classe 'active' do cabeçalho quando a página é carregada
    document.querySelector('.header').classList.remove('active');
    }else {
    // Se o cabeçalho não estiver ativo, adiciona a classe 'active'
    document.querySelector('.header').classList.add('active');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const loginBtn = document.getElementById("login-btn");
    if (loginBtn) {
        loginBtn.addEventListener("click", function () {
            window.location.href = "/cadastro";
        });
    }
});
