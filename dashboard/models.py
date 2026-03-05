from django.db import models
import socket

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
    hostname = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'attack_logs'
        managed = False

    def get_src_hostname(self):
        """Get hostname from source IP using reverse DNS"""
        if self.hostname:
            return self.hostname
        try:
            if self.src_ip:
                hostname, _, _ = socket.gethostbyaddr(self.src_ip)
                return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            pass
        return self.src_ip
    
    def get_dst_hostname(self):
        """Get hostname from destination IP using reverse DNS"""
        try:
            if self.dst_ip:
                hostname, _, _ = socket.gethostbyaddr(self.dst_ip)
                return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            pass
        return self.dst_ip if self.dst_ip else "-"

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
    hostname = models.CharField(max_length=255, null=True, blank=True)  # Hostname dari attack
    instance_id = models.CharField(max_length=50, null=True, blank=True)  # Instance ID
    created_at = models.DateTimeField(auto_now_add=True)
    blocked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ip_block'
        managed = True
        ordering = ['-created_at']


class InstanceMapping(models.Model):
    """Model untuk menyimpan mapping antara hostname, instance ID, IP, dan security group dari Alibaba Cloud"""
    
    id = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=255, unique=True)  # hostname seperti "iZk1afu5vtecqww9xqgmu1Z"
    instance_id = models.CharField(max_length=50)  # instance ID seperti "i-k1afu5vtecqww9xqgmu1"
    public_ip = models.GenericIPAddressField(null=True, blank=True)  # Public IP seperti "147.139.213.142"
    private_ip = models.GenericIPAddressField(null=True, blank=True)  # Private IP
    security_group_id = models.CharField(max_length=50)  # Security Group ID seperti "sg-k1a9bjzlyjzcse7it3va"
    security_group_name = models.CharField(max_length=100, null=True, blank=True)
    region_id = models.CharField(max_length=50, default='ap-southeast-3')
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'instance_mapping'
        managed = True
        ordering = ['hostname']
    
    def __str__(self):
        return f"{self.hostname} ({self.public_ip}) - {self.security_group_id}"
