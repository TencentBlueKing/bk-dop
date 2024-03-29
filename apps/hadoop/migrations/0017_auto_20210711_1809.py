# Generated by Django 2.2.6 on 2021-07-11 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hadoop', '0016_clusterinfo_zk_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusterinfo',
            name='access_token',
            field=models.CharField(default='null', max_length=128, verbose_name='监控平台对应查询的token,用于查询监控数据'),
        ),
        migrations.AddField(
            model_name='clusterinfo',
            name='bk_data_id',
            field=models.IntegerField(default=0, verbose_name='监控平台对应DATA ID,0代表尚未部署监控'),
        ),
        migrations.AddField(
            model_name='clusterinfo',
            name='bk_group_id',
            field=models.IntegerField(default=0, verbose_name='监控平台对应group_id ,0代表尚未部署监控'),
        ),
        migrations.AddField(
            model_name='clusterinfo',
            name='metric_port',
            field=models.IntegerField(default=29999, verbose_name='监控exporter插件对应的访问端口'),
        ),
    ]
