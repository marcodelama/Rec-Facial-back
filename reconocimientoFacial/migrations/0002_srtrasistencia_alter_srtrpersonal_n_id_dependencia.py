# Generated by Django 4.2.17 on 2024-12-13 17:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reconocimientoFacial', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SrtrAsistencia',
            fields=[
                ('n_id_asistencia', models.BigIntegerField(primary_key=True, serialize=False)),
                ('t_hora_inicio', models.DateTimeField(null=True)),
                ('t_hora_fin', models.DateTimeField(null=True)),
                ('c_estado', models.CharField(db_comment='Asistencia del personal (0:No asisti¾, 1:Asisti¾, 2:Tardanza).', max_length=1, null=True)),
                ('d_fecha', models.DateField(null=True)),
            ],
            options={
                'db_table': 'srtr_asistencia',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='srtrpersonal',
            name='n_id_dependencia',
            field=models.ForeignKey(db_column='n_id_dependencia', on_delete=django.db.models.deletion.CASCADE, to='reconocimientoFacial.srthdependencia'),
        ),
    ]