# **🎓 Vocari – Plataforma de Orientación Vocacional Inteligente**

Vocari es una aplicación web desarrollada en **Django + PostgreSQL**, diseñada para ayudar a los usuarios a descubrir su perfil vocacional mediante un test breve, dinámico y altamente preciso.  
El sistema analiza las respuestas, determina un perfil profesional, traduce el resultado automáticamente al inglés mediante una API externa y sugiere cursos relacionados.

Incluye un **panel administrativo**, sistema de consultas, API REST, operaciones CRUD completas, validación avanzada de formularios, AJAX, almacenamiento persistente y un backend escalable.

---

## [Proyecto Desplegado y disponible para uso online](https://proyectodjango-z7f4.onrender.com)

> ⚠️ Los correos solo funcionan en modo local (restricción de Render versión gratuita).

---

# **Lógica del Test Vocacional**
Vocari clasifica al usuario en **4 perfiles principales**:

1. **Tecnológico**  
2. **Creativo**  
3. **Social**  
4. **Analítico**

Las respuestas de cada pregunta suman puntos para cada perfil.  
El sistema selecciona automáticamente el perfil con mayor puntaje.

Luego:

- Genera una **descripción personalizada**
- Llama a la API **MyMemory** para traducirla al inglés
- Genera una lista de **cursos recomendados**
- Traduce también esos cursos

Todo esto ocurre en **tiempo real**.

---

# **Consumo de API Externa**
Vocari emplea la API de traducción **MyMemory** para generar traducciones automáticas del resultado y de los cursos sugeridos.

[**URL utilizada**](https://api.mymemory.translated.net/get?q=%3CTEXTO%3E&langpair=es|en)

Incluye:

- Peticiones con `requests`
- Manejo de errores
- Fallback en caso de fallo de API
- Optimización del texto antes de enviarlo  

---

# **Funcionalidades completas**

## **✔ Test Vocacional**
- 5 preguntas dinámicas  
- Envío mediante POST  
- Análisis automático del perfil  
- Respuesta estructurada  
- Persistencia en base de datos  
- Traducción automática del perfil  
- Traducción automática de los cursos  

---

## **✔ Recomendación de Cursos**
Basado en el perfil detectado.  
Cada curso se traduce al inglés usando la API MyMemory.

---

## **✔ Formulario de Inscripción**
- Validación  
- Guardado en base de datos  
- Envío de email en local  
- Confirmación visual  

---

## **✔ CRUD Completo de Consultas (Panel Admin)**
El staff puede:

- Ver todas las consultas  
- Filtrar  
- Editar  
- Recalcular el perfil automáticamente  
- Eliminar usando modal + AJAX  
- Ver detalles individuales  

---

## **✔ Panel Administrativo**
Incluye:

- Dashboard  
- Listado de consultas  
- Detalle individual  
- Edición  
- Eliminación AJAX  
- Actualización dinámica  

---

## **✔ API REST (Django REST Framework)**

Endpoints:

- `GET /api/consultas/`  
- `POST /api/consultas/`  
- `PUT /api/consultas/<id>/`  
- `DELETE /api/consultas/<id>/`  

---

# **Tecnologías utilizadas**

## **Backend**
- Python 3.12  
- Django 5.0+  
- Django REST Framework  
- PostgreSQL  
- Whitenoise  
- MyMemory API  

## **Frontend**
- HTML5  
- CSS3  
- Bootstrap 5  
- JavaScript (AJAX, Fetch API)  
- Django Templates  

---

# **Capturas de Pantalla**

# Home  
[Ver captura](./img/home.png)

# Test Vocacional  
[Ver captura](./img/test.png)

# Resultado + Cursos  
[Ver captura](./img/resultado.png)

# Formulario de Inscripción  
[Ver captura](./img/inscripcion.png)

# Panel Administrativo  
[Ver captura](./img/panel.png)

---

# 👩‍💻 Autora
**Candela Godoy**  
Desarrolladora Backend / FullStack Jr  
