const form = document.getElementById('form-agendamento');
    const lista = document.getElementById('lista-agendados');

    function salvarAgendamento(agendamento) {
      let agendamentos = JSON.parse(localStorage.getItem('agendamentos') || '[]');
      agendamentos.push(agendamento);
      localStorage.setItem('agendamentos', JSON.stringify(agendamentos));
      exibirAgendamentos();
    }

    function exibirAgendamentos() {
      const agendamentos = JSON.parse(localStorage.getItem('agendamentos') || '[]');
      lista.innerHTML = '';
      agendamentos.forEach(a => {
        const div = document.createElement('div');
        div.classList.add('agendamento');
        div.innerHTML = `
          <strong>Pet:</strong> ${a.pet}
          <strong>Serviço:</strong> ${a.servico}
          <strong>Data:</strong> ${a.data}
          <strong>Horário:</strong> ${a.hora}
        `;
        lista.appendChild(div);
      });
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      const agendamento = {
        pet: form.pet.value,
        servico: form.servico.value,
        data: form.data.value,
        hora: form.hora.value
      };
      salvarAgendamento(agendamento);
      form.reset();
    });

    document.addEventListener('DOMContentLoaded', exibirAgendamentos);
