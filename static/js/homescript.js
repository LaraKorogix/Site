const abrirModal = document.getElementById('abrirModal');
const modal = document.getElementById('modalPet');
const fecharModal = document.getElementById('fecharModal');
const formCadastro = document.getElementById('formCadastroPet');
const mensagemSucesso = document.getElementById('mensagem-sucesso');

abrirModal.onclick = () => {
  modal.style.display = 'block';
  mensagemSucesso.style.display = 'none';
};

fecharModal.onclick = () => {
  modal.style.display = 'none';
};

window.onclick = (e) => {
  if (e.target === modal) {
    modal.style.display = 'none';
  }
};

formCadastro.addEventListener('submit', async function (e) {
  e.preventDefault(); // Impede o envio padrão do formulário

  const formData = new FormData(formCadastro);
  const data = {
    nome_pet: formData.get('nome_pet'),
    especie: formData.get('especie'),
    raca: formData.get('raca')
  };

  try {
    const response = await fetch('/cadastro-pet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      mensagemSucesso.style.display = 'block';
      formCadastro.reset();
    } else {
      alert('Erro ao cadastrar pet. Tente novamente.');
    }
  } catch (error) {
    console.error('Erro na requisição:', error);
    alert('Erro de conexão com o servidor.');
  }
});
