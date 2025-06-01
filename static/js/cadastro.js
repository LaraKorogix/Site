document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.form-box');
    const senha = document.querySelector('input[name="senha"]');
    const confirmarSenha = document.querySelector('input[name="confirmar_senha"]');
    const cpf = document.querySelector('input[name="cpf"]');
    const celular = document.querySelector('input[name="celular"]');

    // Apenas números no CPF e Celular
    [cpf, celular].forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '');
        });
    });

    form.addEventListener('submit', function (e) {
        // Senha com exatamente 8 caracteres
        if (senha.value.length < 4 || senha.value.length > 8) {
            e.preventDefault();
            alert('A senha deve conter entre 4 e 8 caracteres.');
            senha.focus();
            return;
        }

        // Confirmação da senha
        if (senha.value !== confirmarSenha.value) {
            e.preventDefault();
            alert('As senhas não coincidem.');
            confirmarSenha.focus();
            return;
        }

        // CPF com exatamente 11 números
        if (cpf.value.length !== 11) {
            e.preventDefault();
            alert('O CPF deve conter exatamente 11 números.');
            cpf.focus();
            return;
        }

        // Celular com 10 ou 11 números
        if (celular.value.length < 10 || celular.value.length > 11) {
            e.preventDefault();
            alert('O celular deve conter DDD + número (10 ou 11 dígitos).');
            celular.focus();
        }
    });
});
