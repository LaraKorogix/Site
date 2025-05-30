 const lista = document.getElementById('lista-vacinas');

    function exibirVacinas() {
      const agendamentos = JSON.parse(localStorage.getItem('agendamentos') || '[]');
      const vacinas = agendamentos.filter(a => a.servico === 'Vacinação');
      lista.innerHTML = '';

      if (vacinas.length === 0) {
        lista.innerHTML = '<p>Seu pet ainda não tem vacina registrada nesta clínica.</p>';
        return;
      }

      vacinas.forEach(v => {
        const div = document.createElement('div');
        div.classList.add('agendamento');
        div.innerHTML = `
          <strong>Pet:</strong> ${v.pet}<br>
          <strong>Data:</strong> ${v.data}<br>
          <strong>Horário:</strong> ${v.hora}
        `;
        lista.appendChild(div);
      });
    }

    document.addEventListener('DOMContentLoaded', exibirVacinas);