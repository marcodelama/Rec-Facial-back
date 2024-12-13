from django.db import models


# class Migrations(models.Model):
#     id = models.IntegerField(primary_key=True)
#     migration = models.CharField(max_length=255)
#     batch = models.IntegerField()

#     class Meta:
#         managed = False
#         db_table = 'migrations'


# class PasswordResetTokens(models.Model):
#     email = models.CharField(primary_key=True, max_length=255)
#     token = models.CharField(max_length=255)
#     created_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'password_reset_tokens'


# class Sessions(models.Model):
#     id = models.CharField(primary_key=True, max_length=255)
#     user_id = models.BigIntegerField(blank=True, null=True)
#     ip_address = models.CharField(max_length=45, blank=True, null=True)
#     user_agent = models.TextField(blank=True, null=True)
#     payload = models.TextField()
#     last_activity = models.IntegerField()

#     class Meta:
#         managed = False
#         db_table = 'sessions'
# # Unable to inspect table 'srth_asistencia_log_reconocimiento'
# # The error was: ORA-00942: table or view does not exist


# class SrthDependencia(models.Model):
#     n_id_dependencia = models.BigIntegerField(primary_key=True)
#     v_descripcion = models.CharField(max_length=255, blank=True, null=True)
#     v_abreviatura = models.CharField(max_length=70, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'srth_dependencia'


# class SrthEspacio(models.Model):
#     n_id_espacio = models.BigIntegerField(primary_key=True)
#     n_capacidad = models.BigIntegerField(blank=True, null=True, db_comment='Capacidad de personal en el espacio\n')

#     class Meta:
#         managed = False
#         db_table = 'srth_espacio'


# class SrtrActividad(models.Model):
#     n_id_actividad = models.BigIntegerField(primary_key=True)
#     v_nombre = models.CharField(max_length=255, blank=True, null=True)
#     v_descripcion = models.CharField(max_length=755, blank=True, null=True)
#     c_estado = models.CharField(max_length=1, blank=True, null=True, db_comment='Estado de desarrollo de la tarea (0:Por hacer, 1:En curso, 2:Realizada)')
#     c_prioridad = models.CharField(max_length=1, blank=True, null=True, db_comment='Nivel de prioridad de ejecuci¾n de la tarea (1:Baja, 2:Media, 3:Alta)')
#     d_fec_inicio = models.DateField(blank=True, null=True)
#     d_fec_fin = models.DateField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'srtr_actividad'


# class SrtrAsistencia(models.Model):
#     n_id_asistencia = models.BigIntegerField(primary_key=True)
#     t_hora_inicio = models.DateTimeField(blank=True, null=True)
#     t_hora_fin = models.DateTimeField(blank=True, null=True)
#     c_estado = models.CharField(max_length=1, blank=True, null=True, db_comment='Asistencia del personal (0:No asisti¾, 1:Asisti¾, 2:Tardanza).')
#     d_fecha = models.DateField(blank=True, null=True)
#     n_id_personal = models.ForeignKey('SrtrPersonal', models.DO_NOTHING, db_column='n_id_personal')

#     class Meta:
#         managed = False
#         db_table = 'srtr_asistencia'


# class SrtrEvento(models.Model):
#     n_id_evento = models.BigIntegerField(primary_key=True)
#     v_cod_evento = models.CharField(max_length=255, blank=True, null=True)
#     v_nombre = models.CharField(max_length=75, blank=True, null=True)
#     d_fecha_inicio = models.DateField(blank=True, null=True)
#     d_fecha_fin = models.DateField(blank=True, null=True)
#     c_estado = models.CharField(max_length=1, blank=True, null=True, db_comment='0:Por iniciar, 1:En curso, 2:Finalizado\n')

#     class Meta:
#         managed = False
#         db_table = 'srtr_evento'


class SrtrPersonal(models.Model):
    n_id_personal = models.BigIntegerField(primary_key=True)
    v_cod_personal = models.CharField(max_length=7, null=True, unique=True)
    v_nombre = models.CharField(max_length=70, null=True)
    v_apellido_paterno = models.CharField(max_length=70, null=True)
    v_apellido_materno = models.CharField(max_length=70, null=True)
    v_correo_institucional = models.CharField(max_length=80, null=True)
    n_telefono_contacto = models.BigIntegerField(blank=True, null=True)
    n_num_doc = models.BigIntegerField(blank=True, null=True, unique=True)
    v_disponibilidad = models.CharField(max_length=20, null=True, db_comment='Disponibilidad del personal seg·n la fecha')
    c_estado = models.CharField(max_length=1, null=True)
    n_id_dependencia = models.ForeignKey(SrthDependencia, models.DO_NOTHING, db_column='n_id_dependencia')

    def __str__(self) -> str:
        return self.v_nombre


# class SrtrReporte(models.Model):
#     n_id_reporte = models.BigIntegerField(primary_key=True)
#     v_tipo_reporte = models.CharField(max_length=70, blank=True, null=True)
#     d_fecha_generacion = models.DateTimeField(blank=True, null=True)
#     n_id_evento = models.ForeignKey(SrtrEvento, models.DO_NOTHING, db_column='n_id_evento')

#     class Meta:
#         managed = False
#         db_table = 'srtr_reporte'


class SrtrRepositorioImagen(models.Model):
    n_id_rep_imagen = models.BigIntegerField(primary_key=True)
    cl_imagen_biometrica = models.TextField(null=True, upload_to='personas/')
    n_id_personal = models.ForeignKey(SrtrPersonal, on_delete=models.CASCADE, db_column='n_id_personal')

    def __str__(self) -> str:
        return self.n_id_personal


# class SrtrTipoPersonal(models.Model):
#     n_id_tipo_personal = models.BigIntegerField(primary_key=True)
#     v_descripcion = models.CharField(max_length=50, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'srtr_tipo_personal'


# class SrtrTurno(models.Model):
#     n_id_turno = models.BigIntegerField(primary_key=True)
#     t_hora_inicio = models.DateTimeField(blank=True, null=True)
#     t_hora_fin = models.DateTimeField(blank=True, null=True)
#     d_fecha = models.DateField(blank=True, null=True)
#     c_estado = models.CharField(max_length=1, blank=True, null=True, db_comment='(0:Por iniciar, 1: En curso, 2: Finalizado)')
#     n_id_evento = models.ForeignKey(SrtrEvento, models.DO_NOTHING, db_column='n_id_evento')

#     class Meta:
#         managed = False
#         db_table = 'srtr_turno'


# class SrtxEspacioPersonal(models.Model):
#     n_id_espacio_personal = models.BigIntegerField(primary_key=True)
#     n_id_personal = models.ForeignKey(SrtrPersonal, models.DO_NOTHING, db_column='n_id_personal')
#     n_id_espacio = models.ForeignKey(SrthEspacio, models.DO_NOTHING, db_column='n_id_espacio')

#     class Meta:
#         managed = False
#         db_table = 'srtx_espacio_personal'


# class SrtxEspacioTurno(models.Model):
#     n_id_espacio_turno = models.BigIntegerField(primary_key=True)
#     n_id_espacio = models.ForeignKey(SrthEspacio, models.DO_NOTHING, db_column='n_id_espacio')
#     n_id_turno = models.ForeignKey(SrtrTurno, models.DO_NOTHING, db_column='n_id_turno')

#     class Meta:
#         managed = False
#         db_table = 'srtx_espacio_turno'


# class SrtxPersonalActividad(models.Model):
#     id_personal_actividad = models.BigIntegerField(primary_key=True)
#     n_id_personal = models.ForeignKey(SrtrPersonal, models.DO_NOTHING, db_column='n_id_personal')
#     n_id_actividad = models.ForeignKey(SrtrActividad, models.DO_NOTHING, db_column='n_id_actividad')

#     class Meta:
#         managed = False
#         db_table = 'srtx_personal_actividad'


# class SrtxPersonalTipoPersonal(models.Model):
#     n_id_personal_tp = models.BigIntegerField(primary_key=True)
#     n_id_personal = models.ForeignKey(SrtrPersonal, models.DO_NOTHING, db_column='n_id_personal')
#     n_id_tipo_personal = models.ForeignKey(SrtrTipoPersonal, models.DO_NOTHING, db_column='n_id_tipo_personal')

#     class Meta:
#         managed = False
#         db_table = 'srtx_personal_tipo_personal'


# class Users(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     name = models.CharField(max_length=255)
#     email = models.CharField(unique=True, max_length=255)
#     email_verified_at = models.DateTimeField(blank=True, null=True)
#     password = models.CharField(max_length=255)
#     remember_token = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(blank=True, null=True)
#     updated_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'users'