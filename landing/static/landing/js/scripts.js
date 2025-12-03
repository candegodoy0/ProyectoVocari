function displayFlashMessage(message, category) {
    const flashContainer = document.querySelector('#alert-container');
    if (!flashContainer) {
        console.warn('Contenedor de mensajes flash no encontrado. Mostrando mensaje en consola:', message);
        return;
    }

    // limpia mensajes anteriores
    flashContainer.innerHTML = '';

    let title = '';
    if (category === 'success') title = '¡Éxito!';
    else if (category === 'warning') title = 'Atención:';
    else title = 'Error:';

    const alertHtml = `
        <div class="alert alert-${category} alert-dismissible fade show" role="alert">
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    flashContainer.innerHTML = alertHtml;
    flashContainer.scrollIntoView({ behavior: 'smooth' });

}

function toggleButtonState(button, disable, originalText) {
    if (disable) {
        // solo guarda el texto original si no existe
        if (!button.getAttribute('data-original-text')) {
             button.setAttribute('data-original-text', originalText);
        }
        button.disabled = true;
        button.textContent = 'Procesando...';
    } else {
        const textToRestore = button.getAttribute('data-original-text') || originalText;
        button.disabled = false;
        button.textContent = textToRestore;
        // limpia el atributo al restaurar
        button.removeAttribute('data-original-text');
    }
}


document.addEventListener('DOMContentLoaded', function() {
    const formPrincipal = document.querySelector('#formulario-principal');
    const alertContainer = document.querySelector('#alert-container'); // contenedor de mensajes

    // --- manejo del formulario principal (test vocacional) ---
    if (formPrincipal) {
        const submitButton = formPrincipal.querySelector('.btn-enviar');
        // usa el texto actual del boton como respaldo
        let originalTextPrincipal = submitButton ? submitButton.textContent : 'ENVIAR';

        formPrincipal.addEventListener('submit', async (e) => {
            e.preventDefault();

            // deshabilitar boton "enviar"
            if (submitButton) toggleButtonState(submitButton, true, originalTextPrincipal);

            document.querySelectorAll('p.error').forEach(p => p.remove());
            alertContainer.innerHTML = '';

            const formData = new FormData(formPrincipal);
            const url = formPrincipal.action || window.location.href;
            const csrfToken = formData.get('csrfmiddlewaretoken');

            let response = null;
            let data = null;

            try {
                response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                data = await response.json();

                if (response.ok) {
                    // solo mostramos un mensaje si no fue exitoso
                    if (data.status_class !== 'success') {
                        displayFlashMessage(data.user_message, data.status_class);
                    }

                    actualizarResultados(data);

                } else {
                    displayFlashMessage(data.user_message || 'El formulario contiene errores.', 'danger');
                    mostrarErrores(data);
                }

            } catch (error) {
                console.error('Error al enviar el formulario (Fetch):', error);
                displayFlashMessage('Ocurrió un error de conexión. Por favor, intentalo de nuevo.', 'danger');
            } finally {
                // habilitar boton "enviar" al finalizar el ajax
                if (submitButton) toggleButtonState(submitButton, false, originalTextPrincipal);
            }
        });
    }

    // --- manejo del formulario de contacto ---
    const formContactar = document.getElementById('form-contactar');
    if (formContactar) {
    }

});


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

            // formulario de inscripcion
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
            cursosHTML += '<button type="submit" class="btn-inscribir">INSCRIBIRME</button>';
            cursosHTML += '</form>';

        } else {
            cursosHTML += '<p>No se encontraron recomendaciones de cursos.</p>';
        }

        cursosContainer.innerHTML = cursosHTML;

        // --- logica del formulario de inscripcion ---
        const formInscribir = document.querySelector('#form-inscribir');

        if (formInscribir) {
            formInscribir.addEventListener('submit', async (e) => {
                e.preventDefault();

                const submitButton = formInscribir.querySelector('.btn-inscribir');
                // obtener texto original del boton
                const originalTextInscribir = submitButton.getAttribute('data-original-text') || submitButton.textContent;

                // deshabilitar boton "inscribirme"
                if (submitButton) {
                    toggleButtonState(submitButton, true, originalTextInscribir);
                }

                let response = null;
                let data = null;

                const formData = new FormData(formInscribir);
                const csrfToken = formData.get('csrfmiddlewaretoken');
                const url = formInscribir.action;

                try {
                    response = await fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    data = await response.json();

                    if (response.ok && data.success) {
                        // redireccion inmediata
                        window.location.href = data.redirect_url;
                        return;

                    } else {
                        // muestra mensaje de error si la inscripcion falla
                        displayFlashMessage(data.user_message || 'Error al procesar la inscripcion.', 'danger');
                    }

                } catch (error) {
                    console.error('Error al enviar el formulario (Fetch):', error);
                    displayFlashMessage('Ocurrió un error de conexión al inscribir. Por favor, intentalo de nuevo.', 'danger');
                } finally {
                    // habilitar boton "inscribirme" solo si fallo y no hubo redireccion
                    if (submitButton && (!response || !response.ok || !data || !data.success)) {
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

        // saca errores previos
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