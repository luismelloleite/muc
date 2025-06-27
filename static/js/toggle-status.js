document.addEventListener('DOMContentLoaded', function () {
    // Seleciona todos os elementos clicáveis pelo atributo 'data-target-checkbox'
    const toggleTags = document.querySelectorAll('[data-target-checkbox]');

    function performToggle(element) {
        const checkboxSelector = element.dataset.targetCheckbox;
        const checkbox = document.querySelector(checkboxSelector);

        if (!checkbox) {
            console.error('Checkbox alvo não foi encontrado:', checkboxSelector);
            return;
        }

        // Inverte o estado do checkbox
        checkbox.checked = !checkbox.checked;

        // Atualiza a aparência da tag
        if (checkbox.checked) {
            element.innerHTML = '<i class="fas fa-check" aria-hidden="true"></i> Ativo';
            element.classList.remove('danger');
            element.classList.add('success');
        } else {
            element.innerHTML = '<i class="fas fa-times" aria-hidden="true"></i> Inativo';
            element.classList.remove('success');
            element.classList.add('danger');
        }
    }

    toggleTags.forEach(tag => {
        // Evento de clique do mouse
        tag.addEventListener('click', function () {
            performToggle(this);
        });

        // Evento de teclado para acessibilidade (Enter e Espaço)
        tag.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault(); // Previne a rolagem da página ao usar a barra de espaço
                performToggle(this);
            }
        });
    });
});