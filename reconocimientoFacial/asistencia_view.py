from django.shortcuts import render
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

# Importación de librerías externas
import face_recognition as fr
import numpy as np
from datetime import timedelta

# Importación de modelos
from .models import SrtrPersonal, SrtrRepositorioImagen, SrtrImagen, SrtrAsistencia

# drf_yasg
from drf_yasg import openapi
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema

#Tomar asistencia
@csrf_exempt
def asistenciaPersona(request):
    if request.method == 'POST':
        archivo = request.FILES['cl_imagen_biometrica']

        if not archivo:
            return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)
        
        imagenDesconocida = fr.load_image_file(archivo)
        encodingsDesconocido = fr.face_encodings(imagenDesconocida)

        if not encodingsDesconocido:
            return JsonResponse({'mensaje': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        encodingDesconocido = encodingsDesconocido[0]

        try: 
            imagenes = SrtrImagen.objects.all()
            umbral_similitud = 0.6  # Este es el umbral para la similitud de rostros. Ajusta según sea necesario.
            for imagen in imagenes:
                repo = imagen.n_id_rep_imagen
                persona = repo.n_id_personal
                if imagen.cl_encoding:
                    encodingRegistrado = np.array(eval(imagen.cl_encoding))
                    # Compare faces y calcula la distancia
                    resultados = fr.face_distance([encodingRegistrado], encodingDesconocido)

                    # Si la distancia entre rostros es menor que el umbral de similitud, se considera una coincidencia
                    if resultados[0] < umbral_similitud:
                        today = timezone.now().date()
                        asistencia_hoy = SrtrAsistencia.objects.filter(n_id_personal=persona.n_id_personal, d_fecha=today).first()

                        if imagen.d_fecha < (timezone.now() - timedelta(days=365)).date():
                             return JsonResponse({
                                'error': 'La imagen fue registrada hace más de un año. No se puede procesar.',
                            }, status=400)

                        if asistencia_hoy:
                            if asistencia_hoy.t_hora_fin:
                                return JsonResponse({
                                    'mensaje': f'La salida fue marcada a las {asistencia_hoy.t_hora_fin}',
                                    'personal': f'{persona.v_nombre} {persona.v_apellido_paterno} {persona.v_apellido_materno}',
                                    'id_personal': persona.n_id_personal,
                                    'fecha_creacion': imagen.d_fecha
                                })
                            elif asistencia_hoy.t_hora_inicio:
                                diferencia = timezone.now() - asistencia_hoy.t_hora_inicio
                                horas_trabajadas = diferencia.total_seconds()

                                asistencia_hoy.t_hora_fin = timezone.now()
                                asistencia_hoy.c_estado = 2
                                asistencia_hoy.t_horas = timedelta(seconds=horas_trabajadas) 
                                asistencia_hoy.save()

                                mensaje = f'Salida marcada. Horas registradas: {timedelta(seconds=horas_trabajadas)} para {persona.n_num_doc}: {persona.v_nombre}, {persona.v_apellido_paterno}'
                                personal = f'{persona.v_nombre} {persona.v_apellido_paterno} {persona.v_apellido_materno}'
                                id_personal = persona.n_id_personal
                                
                                return JsonResponse({'mensaje': mensaje, 'personal': personal, 'id_personal': id_personal, 'fecha_creacion': imagen.d_fecha}, status=200)
                        else:
                            asistencia = SrtrAsistencia(
                                t_hora_inicio = timezone.now(),
                                c_estado = 1,
                                d_fecha = today,
                                n_id_personal = persona
                            )
                            asistencia.save()
                                
                            response_data = {
                                'mensaje': f'Asistencia registrada de {persona.v_nombre} {persona.v_apellido_paterno}',
                                'personal': f'{persona.v_nombre} {persona.v_apellido_paterno} {persona.v_apellido_materno}',
                                'id_personal': persona.n_id_personal,
                                'fecha_creacion_imagen': imagen.d_fecha
                            }
                            return JsonResponse(response_data, status=200)
            
            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)