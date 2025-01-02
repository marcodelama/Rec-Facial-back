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
from .models import SrtrPersonal, SrtrRepositorioImagen, SrtrImagen, SrthDependencia, SrtrAsistencia

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

dependencia_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'n_id_dependencia': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID de la dependencia'),
        'v_descripcion': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción de la dependencia'),
        'v_abreviatura': openapi.Schema(type=openapi.TYPE_STRING, description='Abreviatura de la dependencia'),
    }
)

dependencia_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id_dependencia': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID de la dependencia'),
        'nombre': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la dependencia'),
        'abreviatura': openapi.Schema(type=openapi.TYPE_STRING, description='Abreviatura de la dependencia'),
    }
)

# verDependencias
@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Obtiene la lista de todas las dependencias",
    operation_summary="Listar Dependencias",
    tags=['Dependencias']
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=dependencia_schema,
                    description='Lista de dependencias'
                ),
                'size': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Cantidad total de dependencias'
                )
            }
        ),
        405: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
            }
        )
    },
)

@csrf_exempt
def verDependencias(request):
    if request.method == 'GET':
        dependencias = SrthDependencia.objects.all()
        dependenciasData = []
        for dependencia in dependencias:
            dependenciaData = {
                'n_id_dependencia': dependencia.n_id_dependencia,
                'v_descripcion': dependencia.v_descripcion,
                'v_abreviatura': dependencia.v_abreviatura,
            }
            dependenciasData.append(dependenciaData)

        size = len(dependenciasData)
        return JsonResponse({'data': dependenciasData, 'size': size})
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)

# Vista de Personal
@api_view(['GET'])
@swagger_auto_schema(
    operation_description="Obtiene la lista de todo el personal con sus datos, imágenes y dependencias",
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
                            'dependencia': dependencia_data_schema,
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
        personal = SrtrPersonal.objects.all()
        personaData = []

        for persona in personal:
            dependencia = persona.n_id_dependencia
            repoImagen = SrtrRepositorioImagen.objects.filter(n_id_personal=persona.n_id_personal).first()
            imagen = None

            if repoImagen and repoImagen.n_id_rep_imagen:
                imagen = SrtrImagen.objects.filter(n_id_rep_imagen=repoImagen.n_id_rep_imagen).first()

            imagenes_data = {
                'id_imagen': imagen.n_id_imagen if imagen else None,
                'imagen_url': request.build_absolute_uri(f'/media/{imagen.cl_imagen_biometrica}') if imagen else None,
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
            'n_id_dependencia': openapi.Schema(type=openapi.TYPE_NUMBER, description='ID de la dependencia'),
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
        idDependencia = request.POST.get('n_id_dependencia')
        archivo = request.FILES.get('cl_imagen_biometrica')

        if not nombre or not archivo or not numDni or not apellidoPaterno or not apellidoMaterno or not telefono or not correo:
            return JsonResponse({'error': 'Hay datos que aun no se han proporcionado'}, status=400)

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
            encoding = np.array(encodings[0]).tolist()

            id_personal = SrtrPersonal.objects.get(n_id_personal=idPersonal)
            
            repoImagen = SrtrRepositorioImagen(
                n_id_personal = id_personal
            )
            repoImagen.save()

            repositorio = SrtrRepositorioImagen.objects.filter(n_id_personal = idPersonal).first()
            idRepositorio = SrtrRepositorioImagen.objects.get(n_id_rep_imagen = repositorio.n_id_rep_imagen)

            imagen = SrtrImagen(
                cl_imagen_biometrica = archivo,
                cl_encoding = encoding,
                n_id_rep_imagen = idRepositorio
            )
            imagen.save()
            
            return JsonResponse({'mensaje': f'Imagen registrada para {idPersonal}'}, status=201)
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
            for imagen in imagenes:
                repo = imagen.n_id_rep_imagen
                persona = repo.n_id_personal
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
                                return JsonResponse({'mensaje': f'Salida marcada para {persona.n_num_doc}: {persona.v_nombre}, {persona.v_apellido_paterno}'}, status=200)
                        else:
                            asistencia = SrtrAsistencia(
                                t_hora_inicio = timezone.now(),
                                c_estado = 1,
                                d_fecha = today,
                                n_id_personal = persona
                            )
                            asistencia.save()
                                
                            response_data = {'mensaje': f'Asistencia registrada de {persona.v_nombre, persona.v_apellido_paterno}',}
                            return JsonResponse(response_data, status=200)

            
            return JsonResponse({'mensaje': 'Rostro no reconocido'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrio un error inesperado: {e}'}, status=500)
    
    return JsonResponse({'mensaje': 'Método no permitido'}, status=405)