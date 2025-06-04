// static/js/servicos.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-agendamento');
    const listaAgendadosUL = document.getElementById('lista-agendados'); // Renomeado para clareza

    if (form) { // Garante que o formulário existe na página
        form.addEventListener('submit', function (e) {
            e.preventDefault(); // Impede a submissão padrão do formulário

            // Pega os valores usando os IDs CORRETOS do HTML
            // Estes serão os IDs (números) para pet e serviço
            const petId = document.getElementById('pet_id_select').value;
            const servicoId = document.getElementById('servico_id_select').value;
            const data = document.getElementById('data_agendamento').value;
            const hora = document.getElementById('hora_agendamento').value;

            console.log("Dados coletados do formulário:", { petId, servicoId, data, hora });

            if (!petId || !servicoId || !data || !hora) {
                alert("Por favor, preencha todos os campos obrigatórios!");
                return;
            }

            // Prepara os dados para enviar. Como o backend espera 'request.form',
            // vamos usar FormData para simular um envio de formulário padrão.
            const formData = new FormData();
            formData.append('pet_id', petId);
            formData.append('servico_id', servicoId);
            formData.append('data', data);
            formData.append('hora', hora);

            // Envia os dados para o backend Flask usando fetch
            fetch(form.action, { // form.action pega a URL do atributo 'action' do form
                method: 'POST',
                body: formData // Não precisa de 'Content-Type' header quando usa FormData com fetch
            })
            .then(response => {
                // O backend redireciona em caso de sucesso ou falha na validação.
                // Se a requisição fetch chegar aqui com response.ok, significa que o POST foi aceito,
                // mas o redirect do Flask será seguido pelo navegador, não pelo fetch diretamente
                // a menos que você configure 'redirect: error' ou 'redirect: manual'.
                // Para formulários HTML que esperam um redirect, a abordagem mais simples
                // é deixar o formulário submeter normalmente se não houver erros de validação no cliente.
                // Contudo, se você quer uma SPA-like experience, você precisa que o backend retorne JSON.

                // Por ora, vamos assumir que o redirect do Flask cuidará de atualizar a página.
                // Se o redirect ocorrer, este .then() pode não ser totalmente executado da forma esperada
                // antes da nova página carregar.

                if (response.ok) { // Se o backend retornasse um JSON de sucesso (status 200)
                    console.log("Agendamento enviado, esperando redirect do servidor.");
                    // Se você quiser atualizar a UI aqui ANTES do redirect ou se o backend retornasse JSON:
                    // return response.json(); // Supondo que o backend retorna JSON de sucesso
                    
                    // COMO O BACKEND ATUAL FAZ REDIRECT, VAMOS RECARREGAR A PÁGINA PARA VER A ATUALIZAÇÃO
                    // OU MELHOR, DEIXAR O REDIRECT DO FLASK FAZER SEU TRABALHO.
                    // Para forçar o comportamento padrão após um POST bem-sucedido no fetch,
                    // você pode fazer o redirect no cliente se o backend retornar um JSON de sucesso:
                    // Ex: if (data.success) window.location.href = data.redirect_url;
                    
                    // Se o backend está configurado para redirecionar, o JavaScript não precisa fazer muito aqui
                    // além de talvez limpar o formulário. O navegador seguirá o redirect.
                    // Se não houvesse redirect no backend e ele retornasse JSON:
                    // adicionarItemNaLista(petId, servicoId, data, hora); // Você precisaria dos nomes aqui, não IDs
                    // form.reset();
                    // alert("Agendamento realizado com sucesso!");
                    
                    // Recarregar a página para ver o agendamento na lista atualizada pelo servidor
                    // Isso é uma forma simples de garantir que a lista está correta após o POST.
                    // Idealmente, o backend retornaria os dados do agendamento e você os adicionaria dinamicamente.
                    window.location.reload(); 
                    return { success: true }; // Apenas para o fluxo do .then()
                } else {
                    // Se o backend retornar um erro JSON (ex: status 400, 500)
                    return response.json().then(errData => {
                        throw new Error(errData.erro || 'Erro desconhecido ao agendar.');
                    });
                }
            })
            // .then(data => { // Se o backend retornasse JSON com os dados do agendamento
            //     if (data && data.success) {
            //         // Lógica para pegar os nomes de pet e serviço se necessário para exibir na UI
            //         // adicionarItemNaLista(data.agendamento.nome_pet, data.agendamento.nome_servico, data.agendamento.data, data.agendamento.hora);
            //         // form.reset();
            //     }
            // })
            .catch(error => {
                console.error('Erro ao enviar agendamento:', error);
                alert(error.message); // Exibe a mensagem de erro específica
            });
        });
    }

    // Função para adicionar item na lista (se você fosse atualizar a UI via JS)
    // Esta função precisaria dos NOMES do pet e do serviço, não dos IDs.
    // Você teria que fazer o backend retornar esses nomes ou fazer outra requisição para buscá-los.
    // Por simplicidade com o redirect atual do Flask, essa função não será chamada diretamente após o fetch.
    // function adicionarItemNaLista(nomePet, nomeServico, data, hora) {
    //     const nenhumAgendamento = document.getElementById('nenhum-agendamento');
    //     if (nenhumAgendamento) {
    //         nenhumAgendamento.remove();
    //     }

    //     const li = document.createElement('li');
    //     li.innerHTML = `
    //       <strong>${nomePet}</strong> 
    //       <span>– ${nomeServico} em ${data} às ${hora}</span>
    //     `;
    //     listaAgendadosUL.appendChild(li);
    // }
});