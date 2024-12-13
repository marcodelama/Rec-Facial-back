from django.shortcuts import render
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

# Importación de librerías externas
import face_recognition as fr
import numpy as np

# Importación de modelos
from .models import SrtrPersonal, SrtrRepositorioImagen, SrthDependencia, SrtrAsistencia

# Registro Personal: Modelo SrtrPersonal y SrtrRepositorioImagen
@csrf_exempt
def verDependencias(request):
    if request.method == 'GET':
        dependencias = SrthDependencia.objects.all()
        # personasAsistencia = []
        dependenciasData = []
        for dependencia in dependencias:
            # asistencias = persona.asistencias.all()
            dependenciaData = {
                'n_id_dependencia': dependencia.n_id_dependencia,
                'v_descripcion': dependencia.v_descripcion,
                'v_abreviatura': dependencia.v_abreviatura,
                # 'apellido_materno': persona.apellido_materno,
                # 'telefono': persona.telefono,
                # 'direccion': persona.direccion,
                # 'correo': persona.correo,
                # 'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
                # 'asistencias': list(asistencias.values('hora_entrada', 'hora_salida', 'dia_registrado'))  # Las asistencias de la persona
            }

            # personasAsistencia.append(personaData)
            dependenciasData.append(dependenciaData)

        size = len(dependenciasData)

        return JsonResponse({'data': dependenciasData, 'size': size})
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

@cache_page(0)
def verPersonal(request):
    if request.method == 'GET':
        personal = SrtrPersonal.objects.all()
        personaData = []

        for persona in personal:
            dependencia = persona.n_id_dependencia

            imagen = SrtrRepositorioImagen.objects.filter(n_id_personal=persona.n_id_personal).first()

            imagenes_data = {
                'id_imagen': imagen.n_id_rep_imagen if imagen else None,
                'imagen_url': request.build_absolute_uri(imagen.cl_imagen_biometrica) if imagen else None,
            }

            dependencia_data = {
                'id_dependencia': dependencia.n_id_dependencia,
                'nombre': dependencia.v_descripcion,
                'abreviatura': dependencia.v_abreviatura
            }

            personalData = {
                'n_id_personal': persona.n_id_personal,
                'v_cod_personal': persona.v_cod_personal,
                'n_num_doc': persona.n_num_doc,
                'v_nombre': persona.v_nombre,
                'v_apellido_paterno': persona.v_apellido_paterno,
                'v_apellido_materno': persona.v_apellido_materno,
                'v_correo_institucional': persona.v_correo_institucional,
                'n_telefono_contacto': persona.n_telefono_contacto,
                'v_disponibilidad': persona.v_disponibilidad,
                'c_estado': persona.c_estado,
                'imagenes': imagenes_data,
                'dependencia': dependencia_data
            }

            personaData.append(personalData)

        size = len(personaData)

        return JsonResponse({'data': personaData, 'size': size})
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

@csrf_exempt
def registrarPersona(request):
    if request.method == 'POST':
        numDni = request.POST.get('n_num_doc')
        codPersonal = request.POST.get('v_cod_personal')
        apellidoPaterno = request.POST.get('v_apellido_paterno')
        apellidoMaterno = request.POST.get('v_apellido_materno')
        nombre = request.POST.get('v_nombre')
        telefono = request.POST.get('n_telefono_contacto')
        correo = request.POST.get('v_correo_institucional')
        idDependencia = request.POST.get('n_id_dependencia')
        archivo = request.FILES.get('cl_imagen_biometrica')

        if not nombre or not archivo or not numDni or not apellidoPaterno or not apellidoMaterno or not telefono or not correo:
            return JsonResponse({'error': 'Hay datos que aun no se ha proporcionado'}, status=400)

        imagen = fr.load_image_file(archivo)
        encodings = fr.face_encodings(imagen)

        if not encodings:
            return JsonResponse({'error': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        try:
            with transaction.atomic():
                encoding = np.array(encodings[0]).tolist()
                dependencia = SrthDependencia.objects.get(n_id_dependencia=idDependencia)

                personal = SrtrPersonal(
                    v_cod_personal=codPersonal,
                    v_nombre=nombre,
                    v_apellido_paterno=apellidoPaterno,
                    v_apellido_materno=apellidoMaterno,
                    v_correo_institucional=correo,
                    n_telefono_contacto=telefono,
                    n_num_doc=numDni,
                    n_id_dependencia=dependencia
                )
                personal.save()

                datosPersonal = SrtrPersonal.objects.filter(n_num_doc=numDni).first()
                idPersonal = SrtrPersonal.objects.get(n_id_personal=datosPersonal.n_id_personal)

                imagen = SrtrRepositorioImagen(
                    cl_imagen_biometrica=archivo,
                    cl_encoding=encoding,
                    n_id_personal=idPersonal
                )
                imagen.save()

                return JsonResponse({'mensaje': f'Persona registrada => DNI: {numDni}, Nombre: {nombre}'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def registrarImagen(request):
    if request.method == 'POST':
        idPersonal = request.POST.get('n_id_personal')
        archivo = request.FILES['cl_imagen_biometrica']

        if not archivo:
            return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)

        imagen = fr.load_image_file(archivo)
        encodings = fr.face_encodings(imagen)

        if not encodings:
            return JsonResponse({'error': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        try:
            encoding = np.array(encodings[0]).tolist()

            id_personal = SrtrPersonal.objects.get(n_id_personal=idPersonal)

            imagen = SrtrRepositorioImagen(
                cl_imagen_biometrica = archivo,
                cl_encoding = encoding,
                n_id_personal = id_personal
            )
            imagen.save()
            
            return JsonResponse({'mensaje': f'Imagen registrada para {idPersonal}'}, status=201)
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
            imagenes = SrtrRepositorioImagen.objects.all()
            for imagen in imagenes:
                persona = imagen.n_id_personal
                if imagen.cl_encoding:
                    encondingRegistrado = np.array(eval(imagen.cl_encoding))
                    coincidencia = fr.compare_faces([encondingRegistrado], encodingDesconocido)
                    if coincidencia[0]:
                        today = timezone.now().date()
                        asistencia_hoy = SrtrAsistencia.objects.filter(n_id_personal=persona.n_id_personal, d_fecha=today).first()
                        
                        if asistencia_hoy:
                            if asistencia_hoy.t_hora_inicio:
                                asistencia_hoy.t_hora_fin = timezone.now()
                                asistencia_hoy.c_estado = 2
                                asistencia_hoy.save()
                                return JsonResponse({'mensaje': f'Salida marcada para {persona.n_num_doc}: {persona.v_nombre}'}, status=200)
                        else:
                            asistencia = SrtrAsistencia(
                                t_hora_inicio = timezone.now(),
                                c_estado = 1,
                                d_fecha = today,
                                n_id_personal = persona
                            )
                            asistencia.save()
                                
                            response_data = {
                                'mensaje': f'Asistencia registrada',
                            }
                            return JsonResponse(response_data, status=200)

            
            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


# @csrf_exempt
# def asistenciaPersona(request):
#     if request.method == 'POST':
#         archivo = request.FILES['imagen']

#         if not archivo:
#             return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)
        
#         imagenDesconocida = fr.load_image_file(archivo)
#         encodingsDesconocido = fr.face_encodings(imagenDesconocida)

#         if not encodingsDesconocido:
#             return JsonResponse({'mensaje': 'No se detectó ningún rostro en la imagen'}, status=400)
        
#         encodingDesconocido = encodingsDesconocido[0]

#         try: 
#             personas = Persona.objects.all()
#             for persona in personas:
#                 if persona.encoding:
#                     encondingRegistrado = np.array(eval(persona.encoding))
#                     coincidencia = fr.compare_faces([encondingRegistrado], encodingDesconocido)
#                     if coincidencia[0]:
#                         today = timezone.now().date()
#                         asistencia_hoy = Asistencia.objects.filter(id_persona=persona, dia_registrado=today).first()
                        
#                         if asistencia_hoy:
#                             if asistencia_hoy.hora_entrada:
#                                 asistencia_hoy.hora_salida = timezone.now()
#                                 asistencia_hoy.save()
#                                 return JsonResponse({'mensaje': f'Salida marcado para {persona.dni}: {persona.nombre}'}, status=200)
#                         else:
#                             asistencia = Asistencia(
#                                 id_persona=persona
#                             )
#                             asistencia.save()
                            
#                             response_data = {
#                                 'mensaje': f'Asistencia registrada',
#                                 'persona': {
#                                     'nombre': persona.nombre,
#                                     'dni': persona.dni,
#                                     'apellido_paterno': persona.apellido_paterno,
#                                     'apellido_materno': persona.apellido_materno,
#                                     'telefono': persona.telefono,
#                                     'direccion': persona.direccion,
#                                     'correo': persona.correo,
#                                     'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
#                                     'asistencia': {
#                                         'hora_entrada': asistencia.hora_entrada,
#                                         'hora_salida': asistencia.hora_salida,
#                                         'dia_registrado': asistencia.dia_registrado
#                                     }
#                                 }
                            #     'persona': {
                            #         'id_personal': persona.n_id_personal,
                            #         'cod_personal': persona.v_cod_personal,
                            #         'num_dni': persona.n_num_doc,
                            #         'nombre': persona.v_nombre,
                            #         'apellido_paterno': persona.v_apellido_paterno,
                            #         'apellido_materno': persona.v_apellido_materno,
                            #         'telefono': persona.n_telefono_contacto,
                            #         'correo_institucional': persona.v_correo_institucional,
                            #         'imagen': request.build_absolute_uri(imagen.cl_imagen_biometrica) if imagen.cl_imagen_biometrica else None,
                            #         'asistencia': {
                            #         'hora_entrada': asistencia.t_hora_inicio,
                            #         'hora_salida': asistencia.t_hora_fin,
                            #         'dia_registrado': asistencia.d_fecha
                            #         }
                            #     }
                            # return JsonResponse(response_data, status=200)

            
#             return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
#         except Exception as e:
#             return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
#     return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


# @csrf_exempt
# def marcarSalida(request):
#     if request.method == 'POST':
#         archivo = request.FILES['imagen']

#         if not archivo:
#             return JsonResponse({'mensaje': 'Imagen es obligatoria'}, status=400)
        
#         imagenDesconocida = fr.load_image_file(archivo)
#         encodingsDesconocido = fr.face_encodings(imagenDesconocida)

#         if not encodingsDesconocido:
#             return JsonResponse({'mensaje': 'No se detectó ningún rostro en la imagen'}, status=400)
        
#         encodingDesconocido = encodingsDesconocido[0]

#         try:
#             personas = Persona.objects.all()
#             for persona in personas:
#                 if persona.encoding:
#                     encodingRegistrado = np.array(eval(persona.encoding))
#                     coincidencia = fr.compare_faces([encodingRegistrado], encodingDesconocido)

#                     if coincidencia[0]:
#                         asistencia = Asistencia.objects.filter(id_persona=persona, dia_registrado =timezone.now().date()).first()

#                         if asistencia.hora_salida:
#                             return JsonResponse({'mensaje': 'La hora de salida ya fue marcado'}, status=400)
                        
#                         asistencia.hora_salida = timezone.now() 
#                         asistencia.save()
                        
#                         response_data = {
#                             'mensaje': f'Salida registrada',
#                             'persona': {
#                                 'nombre': persona.nombre,
#                                 'dni': persona.dni,
#                                 'apellido_paterno': persona.apellido_paterno,
#                                 'apellido_materno': persona.apellido_materno,
#                                 'telefono': persona.telefono,
#                                 'direccion': persona.direccion,
#                                 'correo': persona.correo,
#                                 'imagen': request.build_absolute_uri(persona.imagen.url) if persona.imagen else None,
#                                 'asistencia': {
#                                     'hora_entrada': asistencia.hora_entrada,
#                                     'hora_salida': asistencia.hora_salida,
#                                     'dia_registrado': asistencia.dia_registrado
#                                 }
#                             }
#                         }
#                         return JsonResponse(response_data, status=200)

#             return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)

#         except Exception as e:
#             return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)