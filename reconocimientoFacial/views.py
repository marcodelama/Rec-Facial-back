from django.shortcuts import render
from django.utils import timezone
import face_recognition as fr
import numpy as np
from django.http import JsonResponse
from .models import Persona, Asistencia
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def holaMundo(request):
    if request.method == 'POST':
        return JsonResponse({'mensaje': 'Hola'}, status=200)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def registrarPersona(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        apellidoPaterno = request.POST.get('apellido_paterno')
        apellidoMaterno = request.POST.get('apellido_materno')
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        correo = request.POST.get('correo')
        archivo = request.FILES['imagen']


        if not nombre or not archivo or not dni or not apellidoPaterno or not apellidoMaterno or not telefono or not correo or not direccion:
            return JsonResponse({'error': 'Hay datos que aun no se ha proporcionado'}, status=400)

        imagen = fr.load_image_file(archivo)
        encodings = fr.face_encodings(imagen)

        if not encodings:
            return JsonResponse({'error': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        try:
            encoding = np.array(encodings[0]).tolist()
            persona = Persona(
                dni = dni,
                apellido_paterno = apellidoPaterno,
                apellido_materno = apellidoMaterno,
                nombre=nombre, 
                telefono = telefono,
                direccion = direccion,
                correo = correo,
                imagen=archivo, 
                encoding=encoding)
            persona.save()
            return JsonResponse({'mensaje': f'Persona registrada => DNI: {dni}, Nombre: {nombre}'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def asistenciaPersona(request):
    if request.method == 'POST':
        archivo = request.FILES['imagen']

        if not archivo:
            return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)
        
        imagenDesconocida = fr.load_image_file(archivo)
        encodingsDesconocido = fr.face_encodings(imagenDesconocida)

        if not encodingsDesconocido:
            return JsonResponse({'mensaje': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        encodingDesconocido = encodingsDesconocido[0]

        try: 
            personas = Persona.objects.all()
            for persona in personas:
                if persona.encoding:
                    encondingRegistrado = np.array(eval(persona.encoding))
                    coincidencia = fr.compare_faces([encondingRegistrado], encodingDesconocido)
                    if coincidencia[0]:
                        today = timezone.now().date()
                        asistencia_hoy = Asistencia.objects.filter(id_persona=persona, dia_registrado=today).first()
                        
                        if asistencia_hoy:
                            if asistencia_hoy.hora_entrada:
                                asistencia_hoy.hora_salida = timezone.now()
                                asistencia_hoy.save()
                                return JsonResponse({'mensaje': f'Salida marcado para {persona.dni}: {persona.nombre}'}, status=200)
                        else:
                            asistencia = Asistencia(
                                id_persona=persona
                            )
                            asistencia.save()
                            
                            response_data = {
                                'mensaje': f'Asistencia registrada',
                                'persona': {
                                    'nombre': persona.nombre,
                                    'dni': persona.dni,
                                    'apellido_paterno': persona.apellido_paterno,
                                    'apellido_materno': persona.apellido_materno,
                                    'telefono': persona.telefono,
                                    'direccion': persona.direccion,
                                    'correo': persona.correo,
                                    'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
                                    'asistencia': {
                                        'hora_entrada': asistencia.hora_entrada,
                                        'hora_salida': asistencia.hora_salida,
                                        'dia_registrado': asistencia.dia_registrado
                                    }
                                }
                            }
                            return JsonResponse(response_data, status=200)

            
            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

@csrf_exempt
def verPersonas(request):
    if request.method == 'GET':
        personas = Persona.objects.all()
        personasAsistencia = []
        for persona in personas:
            asistencias = persona.asistencias.all()

            personaData = {
                'dni': persona.dni,
                'nombre': persona.nombre,
                'apellido_paterno': persona.apellido_paterno,
                'apellido_materno': persona.apellido_materno,
                'telefono': persona.telefono,
                'direccion': persona.direccion,
                'correo': persona.correo,
                'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
                'asistencias': list(asistencias.values('hora_entrada', 'hora_salida', 'dia_registrado'))  # Las asistencias de la persona
            }

            personasAsistencia.append(personaData)

        size = len(personasAsistencia)

        return JsonResponse({'data': personasAsistencia, 'size': size})
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

@csrf_exempt
def marcarSalida(request):
    if request.method == 'POST':
        archivo = request.FILES['imagen']

        if not archivo:
            return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)
        
        imagenDesconocida = fr.load_image_file(archivo)
        encodingsDesconocido = fr.face_encodings(imagenDesconocida)

        if not encodingsDesconocido:
            return JsonResponse({'mensaje': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        encodingDesconocido = encodingsDesconocido[0]

        try:
            personas = Persona.objects.all()
            for persona in personas:
                if persona.encoding:
                    encodingRegistrado = np.array(eval(persona.encoding))
                    coincidencia = fr.compare_faces([encodingRegistrado], encodingDesconocido)

                    if coincidencia[0]:
                        asistencia = Asistencia.objects.filter(id_persona=persona, dia_registrado =timezone.now().date()).first()

                        if asistencia.hora_salida:
                            return JsonResponse({'mensaje': 'La hora de salida ya fue marcado'}, status=400)
                        
                        asistencia.hora_salida = timezone.now() 
                        asistencia.save()
                        
                        response_data = {
                            'mensaje': f'Salida registrada',
                            'persona': {
                                'nombre': persona.nombre,
                                'dni': persona.dni,
                                'apellido_paterno': persona.apellido_paterno,
                                'apellido_materno': persona.apellido_materno,
                                'telefono': persona.telefono,
                                'direccion': persona.direccion,
                                'correo': persona.correo,
                                'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
                                'asistencia': {
                                    'hora_entrada': asistencia.hora_entrada,
                                    'hora_salida': asistencia.hora_salida,
                                    'dia_registrado': asistencia.dia_registrado
                                }
                            }
                        }
                        return JsonResponse(response_data, status=200)

            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)

        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)