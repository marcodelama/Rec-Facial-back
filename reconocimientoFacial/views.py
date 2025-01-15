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

# Esquemas reutilizables
imagen_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id_imagen': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID de la imagen'),
        'imagen_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL de la imagen biométrica'),
    }
)

# Vista de Personal
@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Obtiene la lista de todo el personal con sus datos, imágenes",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'n_id_personal': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID del personal'),
                            'v_cod_personal': openapi.Schema(type=openapi.TYPE_STRING, description='Código del personal'),
                            'n_num_doc': openapi.Schema(type=openapi.TYPE_STRING, description='Número de documento'),
                            'v_nombre': openapi.Schema(type=openapi.TYPE_STRING, description='Nombres'),
                            'v_apellido_paterno': openapi.Schema(type=openapi.TYPE_STRING, description='Apellido paterno'),
                            'v_apellido_materno': openapi.Schema(type=openapi.TYPE_STRING, description='Apellido materno'),
                            'v_correo_institucional': openapi.Schema(type=openapi.TYPE_STRING, description='Correo institucional'),
                            'n_telefono_contacto': openapi.Schema(type=openapi.TYPE_STRING, description='Teléfono de contacto'),
                            'v_disponibilidad': openapi.Schema(type=openapi.TYPE_STRING, description='Disponibilidad'),
                            'c_estado': openapi.Schema(type=openapi.TYPE_STRING, description='Estado'),
                            'imagenes': imagen_schema,
                        }
                    )
                ),
                'size': openapi.Schema(type=openapi.TYPE_NUMBER, description='Cantidad total de registros'),
            }
        ),
        405: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error'),
            }
        ),
    },
    operation_summary="Listar Personal",
    tags=['Personal']
)
@cache_page(0)
def verPersonal(request):
    if request.method == 'GET':
        personal = SrtrPersonal.objects.all().order_by('n_id_personal')
        personaData = []

        for persona in personal:
            repoImagen = SrtrRepositorioImagen.objects.filter(n_id_personal=persona.n_id_personal).first()
            imagen = None

            if repoImagen and repoImagen.n_id_rep_imagen:
                imagen = SrtrImagen.objects.filter(n_id_rep_imagen=repoImagen.n_id_rep_imagen).first()

            imagenes_data = {
                'id_imagen': imagen.n_id_imagen if imagen else None,
                'imagen_url': request.build_absolute_uri(f'/media/{imagen.cl_imagen_biometrica}') if imagen else None,
                'd_fecha': imagen.d_fecha if imagen else None,
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
                'imagenes': imagenes_data
            }

            personaData.append(personalData)

        size = len(personaData)
        return JsonResponse({'data': personaData, 'size': size})
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

# Vista de Registro de Personal
@api_view(['POST'])
@swagger_auto_schema(
    operation_description="Registra una nueva persona con su imagen biométrica",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'n_num_doc': openapi.Schema(type=openapi.TYPE_STRING, description='Número de documento'),
            'v_cod_personal': openapi.Schema(type=openapi.TYPE_STRING, description='Código de personal'),
            'v_apellido_paterno': openapi.Schema(type=openapi.TYPE_STRING, description='Apellido paterno'),
            'v_apellido_materno': openapi.Schema(type=openapi.TYPE_STRING, description='Apellido materno'),
            'v_nombre': openapi.Schema(type=openapi.TYPE_STRING, description='Nombres'),
            'n_telefono_contacto': openapi.Schema(type=openapi.TYPE_STRING, description='Teléfono de contacto'),
            'v_correo_institucional': openapi.Schema(type=openapi.TYPE_STRING, description='Correo institucional'),
            'cl_imagen_biometrica': openapi.Schema(type=openapi.TYPE_FILE, description='Imagen biométrica'),
        },
        required=['n_num_doc', 'v_nombre', 'v_apellido_paterno', 'v_apellido_materno', 'n_telefono_contacto', 
                 'v_correo_institucional', 'cl_imagen_biometrica']
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito'),
            }
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error de validación'),
            }
        ),
        500: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error interno del servidor'),
            }
        ),
    },
    operation_summary="Registrar Personal",
    tags=['Personal']
)

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
        archivo = request.FILES.get('cl_imagen_biometrica')

        if not nombre or not numDni or not apellidoPaterno or not apellidoMaterno or not telefono or not correo:
            return JsonResponse({'error': 'Hay datos que aun no se han proporcionado'}, status=400)

        imagen = fr.load_image_file(archivo)
        encodings = fr.face_encodings(imagen)

        if not encodings:
            return JsonResponse({'error': 'No se detectó ningún rostro en la imagen'}, status=400)
        
        try:
            with transaction.atomic():
                encoding = np.array(encodings[0]).tolist()

                personal = SrtrPersonal(
                    v_cod_personal=codPersonal,
                    v_nombre=nombre,
                    v_apellido_paterno=apellidoPaterno,
                    v_apellido_materno=apellidoMaterno,
                    v_correo_institucional=correo,
                    n_telefono_contacto=telefono,
                    n_num_doc=numDni
                )
                personal.save()

                datosPersonal = SrtrPersonal.objects.filter(n_num_doc=numDni).first()
                idPersonal = SrtrPersonal.objects.get(n_id_personal=datosPersonal.n_id_personal)

                repositorioImagen = SrtrRepositorioImagen(
                    n_id_personal=idPersonal
                )
                repositorioImagen.save()
                
                repositorio = SrtrRepositorioImagen.objects.filter(n_id_personal=idPersonal).first()
                idRepositorio = SrtrRepositorioImagen.objects.get(n_id_rep_imagen=repositorio.n_id_rep_imagen)

                imagen = SrtrImagen(
                    cl_imagen_biometrica=archivo,
                    cl_encoding=encoding,
                    n_id_rep_imagen=idRepositorio
                )
                imagen.save()

                return JsonResponse({'mensaje': f'Persona registrada => DNI: {numDni}, Nombre: {nombre}'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista de Registro de Imagen
@api_view(['POST'])
@swagger_auto_schema(
    operation_description="Registra una nueva imagen biométrica para un personal existente",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'n_id_personal': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID del personal'),
            'cl_imagen_biometrica': openapi.Schema(type=openapi.TYPE_FILE, description='Imagen biométrica'),
        },
        required=['n_id_personal', 'cl_imagen_biometrica']
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito'),
            }
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error de validación'),
            }
        ),
        500: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error interno del servidor'),
            }
        ),
    },
    operation_summary="Registrar Imagen",
    tags=['Imágenes']
)

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
            nuevo_encoding = np.array(encodings[0])

            #Corroborar si el personal presenta imágenes en su registro.
            imagenes_personal = SrtrImagen.objects.filter(
                n_id_rep_imagen__n_id_personal__n_id_personal = idPersonal
            )

            if imagenes_personal.exists():
                coincidencia_encontrada = False
                for img_existente in imagenes_personal:
                    encoding_existente = np.array(eval(img_existente.cl_encoding))
                    distancia = np.linalg.norm(nuevo_encoding - encoding_existente)

                    if distancia < 0.6:  # Mientras más cercano al cero, más semejante es la imagen
                        coincidencia_encontrada = True
                        break

                if not coincidencia_encontrada:
                    return JsonResponse({
                        'error': 'La persona no coincide con las imágenes registradas.',
                    }, status=400)                                                          
                        
            # Verificar si la imagen ya existe para otro personal
            #Parte desde SrtrImagen, hacia el repositorio, luego accede a personal y obtiene el id específico
            todas_imagenes = SrtrImagen.objects.exclude(n_id_rep_imagen__n_id_personal__n_id_personal=idPersonal)
            
            for img_existente in todas_imagenes:
                # Convertir el encoding almacenado de string a array numpy
                encoding_existente = np.array(eval(img_existente.cl_encoding))
                
                # Calcula la distancia entre los encodings
                distancia = np.linalg.norm(nuevo_encoding - encoding_existente)
                
                if distancia < 0.6:
                    return JsonResponse({
                        'error': 'Esta imagen corresponde a otro personal ya registrado',
                        'personal_existente': {
                            'nombre': f"{img_existente.n_id_rep_imagen.n_id_personal.v_nombre} {img_existente.n_id_rep_imagen.n_id_personal.v_apellido_paterno}",
                            'id': img_existente.n_id_rep_imagen.n_id_personal.n_id_personal
                        }
                    }, status=400)

            # Si no hay duplicados, continuar con el registro
            id_personal = SrtrPersonal.objects.get(n_id_personal=idPersonal)
            
            repoImagen = SrtrRepositorioImagen(
                n_id_personal = id_personal
            )
            repoImagen.save()

            repositorio = SrtrRepositorioImagen.objects.filter(n_id_personal = idPersonal).first()
            idRepositorio = SrtrRepositorioImagen.objects.get(n_id_rep_imagen = repositorio.n_id_rep_imagen)

            imagen = SrtrImagen(
                cl_imagen_biometrica = archivo,
                cl_encoding = nuevo_encoding.tolist(),
                n_id_rep_imagen = idRepositorio,
                d_fecha = timezone.now()
            )
            imagen.save()

            persona = SrtrPersonal.objects.filter(n_id_personal = idPersonal).first()
            
            return JsonResponse({'mensaje': f'Imagen registrada para {persona.v_nombre} {persona.v_apellido_paterno} {persona.v_apellido_materno}'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

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
                                'fecha_creacion': imagen.d_fecha
                            }
                            return JsonResponse(response_data, status=200)
            
            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)