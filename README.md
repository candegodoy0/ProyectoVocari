# 🎓 Vocari – Simulador de Orientación Vocacional

Vocari es una plataforma web desarrollada con **Django**, diseñada para ayudar a las personas a descubrir su perfil vocacional mediante un test interactivo, análisis automático y recomendaciones personalizadas de cursos.  

Incluye un sistema completo de administración, métricas internas, API REST y manejo avanzado de formularios con AJAX.

---

## [Demo en vivo](https://proyectodjango-z7f4.onrender.com)

*(El envío de correos está deshabilitado en Render por limitaciones del servicio que se utilizo gratuito, pruebas desde local)*

---

## Funcionalidades principales

### ✔ Test vocacional inteligente  
- 5 preguntas clave basadas en intereses reales.  
- Determina un perfil entre: **Tecnológico**, **Creativo/Artístico**, **Social/Humanístico** o **Científico/Analítico**.  
- Genera una descripción precisa y personalizada.  
- Traducción automática del resultado y de los cursos al inglés.

### ✔ Recomendación de cursos  
- Lista de cursos sugeridos según el perfil.  
- Traducción automática (API externa).  
- Opción de inscripción con envío de email (modo local).

### ✔ Panel administrativo  
- Dashboard para administradores.  
- Listado de consultas con búsqueda, filtros y ordenamiento.  
- Edición de resultados (recalculando perfil).  
- Eliminación con modal de confirmación (AJAX).

### ✔ Formularios avanzados (AJAX)  
- Validación en tiempo real.  
- Mensajes dinámicos.  
- Bloqueos de botones, loaders, gestión completa UX/UI.

### ✔ API REST  
Creada con Django REST Framework:  
- `GET /api/consultas/`  
- `POST /api/consultas/`  
- `PUT /api/consultas/<id>/`  
- `DELETE /api/consultas/<id>/`

---

## Tecnologías utilizadas

**Backend**
- Python 3.12  
- Django 5.2.6  
- Django REST Framework  
- PostgreSQL  
- Whitenoise  
- MyMemory Translation API  

**Frontend**
- HTML + Django Templates  
- CSS (custom)  
- Bootstrap 5  
- Fetch API / AJAX  
- Modales dinámicos (Bootstrap)