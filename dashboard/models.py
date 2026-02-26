from django.db import models

class AttackLog(models.Model):
    id = models.IntegerField(primary_key=True)
    timestamp = models.DateTimeField()
    attack_type = models.CharField(max_length=50)
    src_ip = models.CharField(max_length=45)
    dst_ip = models.CharField(max_length=45, null=True, blank=True)
    src_port = models.IntegerField(null=True, blank=True)
    dst_port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=10, null=True, blank=True)
    severity = models.CharField(max_length=20)
    count = models.IntegerField()
    raw_data = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'attack_logs'
        managed = False

class Alert(models.Model):
    id = models.IntegerField(primary_key=True)
    timestamp = models.DateTimeField()
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    severity = models.CharField(max_length=20)
    attack_count = models.IntegerField()
    threshold = models.IntegerField(null=True)

    class Meta:
        db_table = 'alerts'
        managed = False

class ThresholdConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    alert_type = models.CharField(max_length=50)
    threshold_value = models.IntegerField()
    time_window = models.IntegerField()
    severity = models.CharField(max_length=20)
    is_active = models.BooleanField()
    description = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'threshold_config'
        managed = False


class IpBlock(models.Model):
    """Model untuk menyimpan IP yang akan di-block"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('unblocked', 'Unblocked'),
    ]
    
    id = models.AutoField(primary_key=True)
    src_ip = models.CharField(max_length=45)
    reason = models.CharField(max_length=255)
    attack_count = models.IntegerField(default=0)
    severity = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    security_group_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    blocked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ip_block'
        managed = True
        ordering = ['-created_at']
