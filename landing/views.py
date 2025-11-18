import ssl
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, get_connection
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

from rest_framework import viewsets, views, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import ConsultaSerializer
from .forms import TestForm, ContactoForm
from .models import Consulta


DESCRIPCIONES = {
    "Tecnológico": "Te interesa la tecnología la programación y la innovación.",
    "Creativo/Artístico": "Te atrae la expresión artística y las ideas originales.",
    "Social/Humanístico": "Tenés interés en ayudar a otros y en lo comunitario.",
    "Científico/Analítico": "Te motiva investigar analizar y comprender como funcionan las cosas."
}

CURSOS = {
    "Tecnológico": ["Introducción a Python", "Desarrollo Web", "Electrónica básica"],
    "Creativo/Artístico": ["Diseño Gráfico", "Fotografía Digital", "Edición de video"],
    "Social/Humanístico": ["Oratoria", "Trabajo Social", "Gestión de proyectos comunitarios"],
    "Científico/Analítico": ["Estadística básica", "Laboratorio de ciencias", "Análisis de datos"]
}


def calcular_perfil(data):
    # calcula el perfil vocacional basado en las respuestas del test
    # si hay empate, devuelve todos los perfiles ganadores
    puntajes = {
        "Tecnológico": 0, "Creativo/Artístico": 0, "Social/Humanístico": 0, "Científico/Analítico": 0
    }
    for i in range(1, 6):
        respuesta = data.get(f"q{i}")
        if respuesta in puntajes:
            puntajes[respuesta] += 1

    max_p = max(puntajes.values())
    ganadores = [p for p, v in puntajes.items() if v == max_p]

    return ", ".join(ganadores) if len(ganadores) > 1 else ganadores[0] if ganadores else "Indefinido"


def get_translation(text, target_lang='en'):
    # api externa para traducir texto del español al ingles
    API_URL = "https://api.mymemory.translated.net/get"
    params = {
        'q': text,
        'langpair': f'es|{target_lang}'
    }
    try:
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('responseStatus') == 200 and 'translatedText' in data.get('responseData', {}):
            return data['responseData']['translatedText']
        else:
            print(f"Error en api mymemory: {data.get('responseDetails', 'Error desconocido')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la api de traduccion: {e}")
        return None


def send_contacto_email(nombre, correo, mensaje):
    # envia el correo al administrador cuando un usuario usa el formulario de contacto
    asunto = f"Consulta de contacto desde Vocari | De: {nombre}"
    cuerpo_mensaje = (
        f"Nombre: {nombre}\n"
        f"Correo: {correo}\n\n"
        f"Mensaje:\n{mensaje}\n"
    )

    try:
        send_mail(
            asunto,
            cuerpo_mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        print(f"Correo de contacto enviado exitosamente desde {correo}.")
        return True
    except Exception as e:
        print(f"Error al enviar correo de contacto: {e}")
        return False


def send_confirmation_email(nombre, correo, perfil, descripcion, cursos):
    # envia correos de confirmacion (usuario y admin) con los resultados del test
    lista_cursos_html = "".join(f"<li>{c}</li>" for c in cursos)

    asunto_usuario = f"Informe Vocacional | {nombre}"
    cuerpo_html_usuario = f"""
    <html>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
      <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:10px;">

        <h2 style="color:#333;">Hola {nombre},</h2>
        <p>Gracias por completar el <strong>Test Vocacional</strong>.</p>

        <h3>Perfil obtenido: <strong>{perfil}</strong></h3>
        <p>{descripcion}</p>

        <h3>Cursos recomecomendados:</h3>
        <ul>{lista_cursos_html}</ul>

        <p style="margin-top:20px;">¡Gracias por usar Vocari Project!<br>
        <strong>Equipo Vocari Project</strong></p>
      </div>
    </body>
    </html>
    """

    asunto_admin = f"Nueva evaluación | {perfil} - {nombre}"
    cuerpo_html_admin = f"""
    <html>
    <body style="font-family: Arial;">
      <h2 style="color:#444;">Nuevo informe generado</h2>

      <p><strong>Nombre:</strong> {nombre}</p>
      <p><strong>Correo:</strong> {correo}</p>
      <p><strong>Perfil:</strong> {perfil}</p>
      <p><strong>Descripción:</strong> {descripcion}</p>

      <h3>Cursos recomendados:</h3>
      <ul>{lista_cursos_html}</ul>
    </body>
    </html>
    """

    try:
        context = ssl._create_unverified_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            # correo html al usuario
            msg_user = MIMEMultipart("alternative")
            msg_user["Subject"] = asunto_usuario
            msg_user["From"] = settings.DEFAULT_FROM_EMAIL
            msg_user["To"] = correo
            msg_user.attach(MIMEText(cuerpo_html_usuario, "html", "utf-8"))
            server.send_message(msg_user)

            # correo html al administrador
            msg_admin = MIMEMultipart("alternative")
            msg_admin["Subject"] = asunto_admin
            msg_admin["From"] = settings.DEFAULT_FROM_EMAIL
            msg_admin["To"] = settings.DEFAULT_FROM_EMAIL
            msg_admin.attach(MIMEText(cuerpo_html_admin, "html", "utf-8"))
            server.send_message(msg_admin)

        return True

    except Exception as e:
        print(f"ERROR AL ENVIAR EMAIL VOCARI: {e}")
        return False


def consumir_traduccion_drf(texto):
    url = "https://proyectodjango-z7f4.onrender.com/api/traducir/"
    try:
        response = requests.get(url, params={'texto': texto})
        response.raise_for_status()

        data = response.json()
        return data.get('traduccion')

    except requests.exceptions.RequestException as e:
        print(f"Error al consumir api de traducción drf interna: {e}")
        return None


def index(request):
    # muestra el formulario del test, procesa las respuestas, calcula el perfil
    # y maneja la persistencia y la comunicacion
    perfil = None
    descripcion = None
    cursos = []
    nombre_val = ""
    correo_val = ""

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":
        form = TestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            nombre_val = data["nombre"]
            correo_val = data["correo"]

            # calculo de perfil
            perfil = calcular_perfil(data)
            descripcion = " / ".join(DESCRIPCIONES.get(p, "") for p in perfil.split(", "))

            # determinacion de cursos y traducciones
            seen = set()
            cursos_con_traduccion = []
            cursos_unicos = []

            traduccion_descripcion = consumir_traduccion_drf(descripcion)

            for p in perfil.split(", "):
                for c in CURSOS.get(p, []):
                    if c not in seen:
                        seen.add(c)
                        cursos_unicos.append(c)

                        traduccion_curso = consumir_traduccion_drf(c)

                        cursos_con_traduccion.append({
                            'nombre': c,
                            'traduccion': traduccion_curso
                        })

            # persistencia de datos
            try:
                Consulta.objects.create(
                    nombre=data['nombre'],
                    edad=data['edad'],
                    correo=data['correo'],
                    nivel=data['nivel'],
                    q1=data['q1'], q2=data['q2'], q3=data['q3'], q4=data['q4'], q5=data['q5'],
                    perfil_obtenido=perfil,
                )
                db_status = True
            except Exception as e:
                print(f"Error al guardar la consulta en la base de datos: {e}")
                db_status = False

            # envio de correo y generacion del mensaje para javascript
            email_sent = send_confirmation_email(nombre_val, correo_val, perfil, descripcion, cursos_unicos)

            if email_sent and db_status:
                user_message = "¡Test completado! Tus resultados y guia personalizada han sido enviados a tu correo."
                status_class = "success"
            elif not email_sent:
                user_message = "Test completado pero no pudimos enviar el correo con tus resultados. Revisa tu direccion y contactanos."
                status_class = "warning"
            else:
                user_message = "Test completado. Hubo un error al guardar tu consulta en el sistema. Contacta a soporte."
                status_class = "danger"

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'perfil': perfil,
                    'descripcion': descripcion,
                    'traduccion_descripcion': traduccion_descripcion,
                    'cursos': cursos_con_traduccion,
                    'nombre': nombre_val,
                    'correo': correo_val,
                    'csrf_token': get_token(request),
                    'user_message': user_message,
                    'status_class': status_class
                })

            return render(request, "landing/index.html", {
                "form": form,
                "perfil": perfil,
                "descripcion": descripcion,
                "cursos": cursos_con_traduccion,
                "nombre": nombre_val,
                "correo": correo_val
            })


        else:  # formulario no valido
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'user_message': 'Por favor, revisa los errores en el formulario.'
                }, status=400)

            else:
                form = TestForm(request.POST)
                return render(request, "landing/index.html", {"form": form})

    else:
        form = TestForm()

    return render(request, "landing/index.html", {
        "form": form,
        "perfil": perfil,
        "descripcion": descripcion,
        "cursos": cursos,
        "nombre": nombre_val,
        "correo": correo_val
    })

def inscribir(request):
    # procesa la inscripcion a cursos seleccionados y envia los correos
    if request.method == "POST":
        cursos_seleccionados = request.POST.getlist("cursos")
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")

        lista_html = "".join(f"<li>{c}</li>" for c in cursos_seleccionados)

        asunto_u = f"Inscripción confirmada | {nombre}"
        cuerpo_u = f"""
        <html>
        <body style="font-family:Arial;background:#f4f4f4;padding:20px;">
          <div style="max-width:600px;margin:auto;background:white;padding:20px;border-radius:10px;">

            <h2>Hola {nombre},</h2>
            <p>Tu inscripción fue recibida correctamente.</p>

            <h3>Cursos seleccionados:</h3>
            <ul>{lista_html}</ul>

            <p>Nos contactaremos contigo pronto.<br>
            <strong>Equipo Vocari Project</strong></p>
          </div>
        </body>
        </html>
        """

        asunto_a = f"Inscripción recibida | {nombre}"
        cuerpo_a = f"""
        <html>
        <body style="font-family:Arial;">
            <h2>Nueva inscripción</h2>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Correo:</strong> {correo}</p>
            <h3>Cursos:</h3>
            <ul>{lista_html}</ul>
        </body>
        </html>
        """

        try:
            context = ssl._create_unverified_context()
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as server:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

                msg_user = MIMEMultipart("alternative")
                msg_user["Subject"] = asunto_u
                msg_user["From"] = settings.DEFAULT_FROM_EMAIL
                msg_user["To"] = correo
                msg_user.attach(MIMEText(cuerpo_u, "html", "utf-8"))
                server.send_message(msg_user)

                msg_admin = MIMEMultipart("alternative")
                msg_admin["Subject"] = asunto_a
                msg_admin["From"] = settings.DEFAULT_FROM_EMAIL
                msg_admin["To"] = settings.DEFAULT_FROM_EMAIL
                msg_admin.attach(MIMEText(cuerpo_a, "html", "utf-8"))
                server.send_message(msg_admin)

            print("✅ Correos de inscripción enviados (usuario y admin).")

        except Exception as e:
            print(f"❌ Error al enviar correos de inscripción: {e}")

        user_message = f"¡Inscripción recibida con éxito! Te contactaremos en {correo}."
        return render(request, "landing/inscribir.html", {
            "cursos": cursos_seleccionados,
            "nombre": nombre,
            "correo": correo,
            "success_message": user_message,
            "success_status": True
        })

    return render(request, "landing/inscribir.html", {})

def registro(request):
    # maneja el registro de nuevos usuarios
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, "landing/registro.html", {'form': form})

def login_redirect_view(request):
    # vista que redirige al usuario logueado segun su permiso
    if request.user.is_staff:
        # si es admin va al dashboard
        return redirect('dashboard')
    else:
        # si no es amdin
        return redirect('no_admin_landing')

def no_admin_landing(request):
    # pagina para usuarios logueados que no son admin
    if request.user.is_authenticated:
        return render(request, "landing/no_admin_landing.html")
    else:
        return redirect('index')

def sobre_nosotros(request):
    return render(request, 'landing/sobre_nosotros.html', {})


def contacto(request):
    success_message = None

    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            mensaje = form.cleaned_data['mensaje']

            if send_contacto_email(nombre, correo, mensaje):
                success_message = "¡Mensaje enviado con exito! Te responderemos pronto."
                form = ContactoForm()
            else:
                success_message = "Hubo un error al enviar el mensaje. Intenta mas tarde."

    else:
        form = ContactoForm()

    return render(request, 'landing/contacto.html', {
        'form': form,
        'success_message': success_message
    })


@staff_member_required(login_url='login')
def listado_consultas(request):
    # muestra un listado de todas las consultas guardadas, ordenadas por fecha
    try:
        consultas = Consulta.objects.all().order_by('-id')
        return render(request, "landing/listado_consultas.html", {"consultas": consultas})
    except Exception as e:
        print(f"Error al listar consultas: {e}")
        return render(request, "landing/listado_consultas.html",
                      {"error_message": "Hubo un error al cargar el listado."})


@staff_member_required(login_url='login')
def editar_consulta(request, consulta_id):
    # permite editar una consulta existente y recalcular el perfil
    consulta = get_object_or_404(Consulta, id=consulta_id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = TestForm(request.POST, instance=consulta)

        if form.is_valid():
            data = form.cleaned_data
            perfil_actualizado = calcular_perfil(data)
            consulta.perfil_obtenido = perfil_actualizado
            form.save()

            if is_ajax:
                return JsonResponse({'success': True, 'perfil': perfil_actualizado})
            else:
                return redirect('listado_consultas')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = TestForm(instance=consulta)
    return render(request, 'landing/editar_consulta.html', {'form': form, 'consulta': consulta})


@staff_member_required(login_url='login')
def eliminar_consulta(request, consulta_id):
    # maneja la eliminacion de una consulta especifica
    consulta = get_object_or_404(Consulta, id=consulta_id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        try:
            consulta.delete()
            if is_ajax:
                return JsonResponse({'success': True, 'id': consulta_id, 'message': 'Consulta eliminada.'})
            else:
                return redirect('listado_consultas')
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
            return redirect('listado_consultas')

    return redirect('listado_consultas')


@staff_member_required(login_url='login')
def dashboard(request):
    return render(request, "landing/dashboard.html")


class TraduccionAPIView(views.APIView):

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # maneja las peticiones get para la traduccion
        texto_a_traducir = request.query_params.get('texto', None)

        if not texto_a_traducir:
            return Response(
                {"error": "El parametro 'texto' es obligatorio para la traduccion."},
                status=status.HTTP_400_BAD_REQUEST
            )
        traduccion = get_translation(texto_a_traducir, target_lang='en')

        if traduccion is None:
            return Response(
                {"error": "No se pudo obtener la traduccion de la api externa."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


        return Response({
            "texto_original": texto_a_traducir,
            "traduccion": traduccion
        })


class ConsultaViewSet(viewsets.ModelViewSet):
    # api crud para el modelo consulta
    queryset = Consulta.objects.all().order_by('-fecha_consulta')
    serializer_class = ConsultaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        data = serializer.validated_data
        perfil_calculado = calcular_perfil(data)
        serializer.save(perfil_obtenido=perfil_calculado)

    def perform_update(self, serializer):
        data = serializer.validated_data
        perfil_calculado = calcular_perfil(data)
        serializer.save(perfil_obtenido=perfil_calculado)