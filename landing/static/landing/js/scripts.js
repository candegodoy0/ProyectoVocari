// funcion para manejar el estado del botón (deshabilitar/habilitar)
function toggleButtonState(button, isLoading, originalText) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('loading-state');
        button.textContent = 'Enviando...';
    } else {
        button.disabled = false;
        button.classList.remove('loading-state');
        // restaura el texto original
        button.textContent = originalText;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#formulario-principal');
    const alertContainer = document.querySelector('#alert-container');

    if (form) {
        const submitButton = form.querySelector('.btn-enviar');
        let originalTextPrincipal = submitButton ? submitButton.textContent : 'ENVIAR';

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (submitButton) toggleButtonState(submitButton, true, originalTextPrincipal);

            document.querySelectorAll('p.error').forEach(p => p.remove());
            alertContainer.innerHTML = '';

            const formData = new FormData(form);
            const url = form.action || window.location.href;
            const csrfToken = formData.get('csrfmiddlewaretoken');

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    displayFlashMessage(data.user_message, data.status_class);
                    actualizarResultados(data);
                } else {
                    const errorData = await response.json();
                    displayFlashMessage(errorData.user_message || 'El formulario contiene errores.', 'danger');
                    mostrarErrores(errorData);
                }

            } catch (error) {
                console.error('Error al enviar el formulario (Fetch):', error);
                displayFlashMessage('Ocurrió un error de conexión. Por favor, inténtalo de nuevo.', 'danger');
            } finally {
                if (submitButton) toggleButtonState(submitButton, false, originalTextPrincipal);
            }
        });
    }
});

function displayFlashMessage(message, type) {
    const alertContainer = document.querySelector('#alert-container');
    if (!alertContainer) return;

    let title = '';
    if (type === 'success') title = '¡Éxito!';
    else if (type === 'warning') title = 'Atención:';
    else title = 'Error:';

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.innerHTML = alertHtml;
    alertContainer.scrollIntoView({ behavior: 'smooth' });
}

function actualizarResultados(data) {
    const perfilContainer = document.querySelector('.resultado-item:first-child .resultado-contenido');
    const cursosContainer = document.querySelector('.resultado-item:last-child .resultado-contenido');

    if (perfilContainer) {
        let perfilHTML = '';

        if (data.perfil) {
            perfilHTML += `<p><strong>Tu perfil profesional es: ${data.perfil.toUpperCase()}</strong></p>`;
            perfilHTML += `<p>${data.descripcion}</p>`;

            if (data.traduccion_descripcion) {
                perfilHTML += `<p class="text-muted fst-italic">Traducción (EN): ${data.traduccion_descripcion}</p>`;
            }
        } else {
            perfilHTML += '<p>Acá se mostrará el perfil obtenido y una breve descripción del mismo.</p>';
        }

        perfilContainer.innerHTML = perfilHTML;
    }

    if (cursosContainer) {
        let cursosHTML = '';

        if (data.cursos && data.cursos.length > 0) {
            cursosHTML += '<h3>Los cursos que te recomendamos son:</h3>';

            cursosHTML += `<form action="/inscribir/" method="post" id="form-inscribir">`;
            cursosHTML += `<input type="hidden" name="csrfmiddlewaretoken" value="${data.csrf_token || ''}">`;
            cursosHTML += `<input type="hidden" name="nombre" value="${data.nombre || ''}">`;
            cursosHTML += `<input type="hidden" name="correo" value="${data.correo || ''}">`;

            cursosHTML += '<div class="lista-cursos">';

            data.cursos.forEach(item => {
                cursosHTML += `
                    <label class="curso-item">
                        <input type="checkbox" name="cursos" value="${item.nombre}">
                        ${item.nombre}
                        ${item.traduccion ? `<span class="text-muted fst-italic">(${item.traduccion})</span>` : ''}
                    </label><br>
                `;
            });

            cursosHTML += '</div>';
            cursosHTML += '<button type="submit" class="btn-inscribir" data-original-text="INSCRIBIRME">INSCRIBIRME</button>';
            cursosHTML += '</form>';

        } else {
            cursosHTML += '<p>No se encontraron recomendaciones de cursos.</p>';
        }

        cursosContainer.innerHTML = cursosHTML;

        const formInscribir = document.querySelector('#form-inscribir');

        if (formInscribir) {
            formInscribir.addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitButton = formInscribir.querySelector('.btn-inscribir');
                const originalTextInscribir = submitButton.getAttribute('data-original-text');

                if (submitButton) {
                    toggleButtonState(submitButton, true, originalTextInscribir);
                    submitButton.textContent = 'Procesando...';
                }

                const formData = new FormData(formInscribir);
                const csrfToken = formData.get('csrfmiddlewaretoken');
                const url = formInscribir.action;

                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    const data = await response.json();

                    if (response.ok) {
                        displayFlashMessage(data.user_message || 'Inscripción procesada correctamente.', 'success');
                    } else {
                        displayFlashMessage(data.user_message || 'Error al procesar la inscripción.', 'danger');
                    }

                } catch (error) {
                    console.error('Error al enviar el formulario (Fetch):', error);
                    displayFlashMessage('Ocurrió un error de conexión al inscribir. Por favor, inténtalo de nuevo.', 'danger');
                } finally {
                    if (submitButton) {
                        toggleButtonState(submitButton, false, originalTextInscribir);
                    }
                }
            });
        }

        document.getElementById('resultado')?.scrollIntoView({ behavior: 'smooth' });
    }
}

function mostrarErrores(errorData) {
    for (const [campo, errores] of Object.entries(errorData.errors || {})) {

        document.querySelectorAll(`[name="${campo}"]`).forEach(input => {
            input.closest('.campo')?.querySelectorAll('p.error').forEach(p => p.remove());
            input.closest('.pregunta')?.querySelectorAll('p.error').forEach(p => p.remove());
        });

        const inputElement = document.querySelector(`[name="${campo}"]`);

        if (inputElement) {
            const campoDiv = inputElement.closest('.campo') || inputElement.closest('.pregunta');

            errores.forEach(errorText => {
                const errorP = document.createElement('p');
                errorP.className = 'error';
                errorP.textContent = errorText;
                campoDiv?.appendChild(errorP);
            });
        }
    }
}
