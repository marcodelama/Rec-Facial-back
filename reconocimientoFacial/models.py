from django.db import models

# Create your models here.
# class Persona(models.Model):
#     dni = models.CharField(max_length=20, unique=True)
#     apellido_paterno = models.CharField(max_length=100)
#     apellido_materno = models.CharField(max_length=100)
#     nombre = models.CharField(max_length=100)
#     telefono = models.CharField(max_length=100)
#     direccion = models.CharField(max_length=100)
#     correo = models.CharField(max_length=100)
#     # imagen = models.ImageField(upload_to='personas/')
#     encoding = models.TextField(null=True)

#     def __str__(self) -> str:
#         return self.nombre
    

# class Asistencia(models.Model):
#     id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='asistencias')
#     hora_entrada = models.DateTimeField(auto_now_add=True)
#     hora_salida = models.DateTimeField(null=True)
#     dia_registrado = models.DateField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.id_persona    

class SrthDependencia(models.Model):
    n_id_dependencia = models.BigIntegerField(primary_key=True)
    v_descripcion = models.CharField(max_length=255, null=True)
    v_abreviatura = models.CharField(max_length=70, null=True)
    
    class Meta:
        db_table = 'SRTH_DEPENDENCIA'

class SrtrPersonal(models.Model):
    n_id_personal = models.BigIntegerField(primary_key=True)
    v_cod_personal = models.CharField(max_length=7)
    v_nombre = models.CharField(max_length=70, null=True)
    v_apellido_paterno = models.CharField(max_length=70, null=True)
    v_apellido_materno = models.CharField(max_length=70, null=True)
    v_correo_institucional = models.CharField(max_length=80, null=True)
    n_telefono_contacto = models.BigIntegerField(null=True)
    n_num_doc = models.BigIntegerField(null=True)
    v_disponibilidad = models.CharField(max_length=20, null=True, db_comment='Disponibilidad del personal seg·n la fecha')
    c_estado = models.CharField(max_length=1, null=True)
    n_id_dependencia = models.ForeignKey(SrthDependencia, db_column='n_id_dependencia',  on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'SRTR_PERSONAL'
        
class SrtrAsistencia(models.Model):
    n_id_asistencia = models.BigIntegerField(primary_key=True)
    t_hora_inicio = models.DateTimeField(null=True)
    t_hora_fin = models.DateTimeField(null=True)
    c_estado = models.CharField(max_length=1, null=True, db_comment='Asistencia del personal (0:No asisti¾, 1:Asisti¾, 2:Tardanza).')
    d_fecha = models.DateField(null=True)
    t_horas = models.DurationField(null=True)
    n_id_personal = models.ForeignKey('SrtrPersonal', on_delete=models.CASCADE, db_column='n_id_personal')

    class Meta:
        managed = False
        db_table = 'srtr_asistencia'

class SrtrRepositorioImagen(models.Model):
    n_id_rep_imagen = models.BigIntegerField(primary_key=True)
    n_id_personal = models.ForeignKey(SrtrPersonal, on_delete=models.CASCADE, db_column='n_id_personal')

    class Meta:
        db_table = 'SRTR_REPOSITORIO_IMAGEN'

class SrtrImagen(models.Model):
    n_id_imagen = models.BigIntegerField(primary_key=True)
    cl_imagen_biometrica = models.ImageField(upload_to='personas/')
    cl_encoding = models.TextField(blank=True, null=True)
    d_fecha = models.DateField(null=False)
    n_id_rep_imagen = models.ForeignKey('SrtrRepositorioImagen', on_delete=models.CASCADE, db_column='n_id_rep_imagen')

    class Meta:
        managed = False
        db_table = 'srtr_imagen'