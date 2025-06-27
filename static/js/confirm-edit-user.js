document.addEventListener('DOMContentLoaded', function() {
    const userForm = document.getElementById('user-form');

    // Se o formulário não existir nesta página, não faz nada.
    if (!userForm) {
        return;
    }

    const customConfirmModal = document.getElementById('customConfirmModal');
    const customConfirmOkButton = document.getElementById('customConfirmOk');
    const customConfirmCancelButton = document.getElementById('customConfirmCancel');

    // Obtém os IDs dos atributos data-* do formulário.
    // Esses atributos devem ser definidos no template HTML.
    const loggedInUserIdString = userForm.dataset.loggedInUserId;
    const editingUserIdString = userForm.dataset.editingUserId;

    // Verifica se os atributos de dados necessários estão presentes.
    if (typeof loggedInUserIdString === 'undefined' || typeof editingUserIdString === 'undefined') {
        console.warn('Atributos data-logged-in-user-id ou data-editing-user-id não encontrados no formulário.');
        return;
    }

    const loggedInUserId = parseInt(loggedInUserIdString, 10);
    // editingUserId será 0 (ou NaN se o atributo estiver ausente/inválido, mas o default '0' no template ajuda) para um novo usuário.
    const editingUserId = parseInt(editingUserIdString, 10);

    // Garante que os elementos do modal existem antes de adicionar listeners.
    if (customConfirmModal && customConfirmOkButton && customConfirmCancelButton) {
        userForm.addEventListener('submit', function(event) {
            // Condição para mostrar o modal:
            // 1. Estamos editando um usuário existente (editingUserId > 0).
            // 2. O usuário logado é o mesmo que está sendo editado.
            if (editingUserId > 0 && loggedInUserId > 0 && loggedInUserId === editingUserId) {
                event.preventDefault(); // Impede a submissão padrão do formulário.
                customConfirmModal.style.display = 'flex'; // Mostra o modal.
            }
            // Caso contrário, o formulário é submetido normalmente.
        });

        // Listener para o botão "Confirmar" do modal.
        customConfirmOkButton.addEventListener('click', function() {
            customConfirmModal.style.display = 'none'; // Esconde o modal.
            userForm.submit(); // Submete o formulário programaticamente.
        });

        // Listener para o botão "Cancelar" do modal.
        customConfirmCancelButton.addEventListener('click', function() {
            customConfirmModal.style.display = 'none'; // Esconde o modal.
            // A submissão do formulário já foi prevenida, então não é necessário fazer mais nada.
        });
    } else {
        console.warn('Elementos do modal de confirmação customizado não foram encontrados.');
    }
});
