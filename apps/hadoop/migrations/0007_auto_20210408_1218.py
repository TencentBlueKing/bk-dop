# Generated by Django 2.2.6 on 2021-04-08 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hadoop', '0006_clusterinfo_add_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='hadooptaskrecord',
            name='op_user',
            field=models.CharField(default='unknown', max_length=32, verbose_name='操作者'),
        ),
        migrations.AddField(
            model_name='hadooptaskrecord', name='task_kwargs', field=models.TextField(default='', verbose_name='任务参数'),
        ),
        migrations.AlterField(
            model_name='clusterinfo',
            name='cluster_status',
            field=models.IntegerField(
                choices=[
                    (0, '已下线'),
                    (1, '部署中'),
                    (2, '部署异常'),
                    (3, '上线中'),
                    (4, '集群变更中'),
                    (5, '集群异常'),
                    (6, '集群录入中'),
                    (7, '集群录入异常'),
                    (99, '未知状态'),
                ],
                default=99,
                verbose_name='集群状态',
            ),
        ),
        migrations.AlterField(
            model_name='hadooptaskrecord',
            name='task_type',
            field=models.IntegerField(
                choices=[
                    (0, '其他'),
                    (1, 'hdfs集群部署'),
                    (2, 'yarn集群部署'),
                    (3, 'hdfs_yarn集群部署'),
                    (4, 'hdfs_datanode节点扩容'),
                    (5, 'hdfs_datanode节点缩容'),
                    (6, 'yarn_nodemanager节点扩容'),
                    (7, 'yarn_nodemanager节点缩容'),
                    (8, 'hdfs_datanode多磁盘扩容'),
                    (9, '集群录入检测'),
                ],
                default=0,
                verbose_name='任务类型',
            ),
        ),
    ]