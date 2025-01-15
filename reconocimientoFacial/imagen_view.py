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