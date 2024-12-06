from django.db import models

# Create your models here.
class Persona(models.Model):
    dni = models.CharField(max_length=20, unique=True)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='personas/')
    encoding = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.nombre
    

class Asistencia(models.Model):
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='asistencias')
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(blank=True, null=True)
    dia_registrado = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.id_persona    