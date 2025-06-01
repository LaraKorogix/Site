document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form-agendamento');
  const lista = document.getElementById('lista-agendados');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const pet = document.getElementById('pet').value;
    const servico = document.getElementById('servico').value;
    const data = document.getElementById('data').value;
    const hora = document.getElementById('hora').value;

    if (!pet || !servico || !data || !hora) {
      alert("Preencha todos os campos!");
      return;
    }

    // Remove a mensagem "Nenhum serviço agendado ainda" se existir
    const nenhumAgendamento = document.getElementById('nenhum-agendamento');
    if (nenhumAgendamento) {
      nenhumAgendamento.remove();
    }

    // Cria item de lista estilizado
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${pet}</strong>
      <span>– ${servico} em ${data} às ${hora}</span>
    `;

    lista.appendChild(li);

    // Limpa o formulário após submissão
    form.reset();
  });
});
