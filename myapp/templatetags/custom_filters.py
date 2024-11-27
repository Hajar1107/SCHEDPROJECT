from django import template
from myapp.models import PerformanceMetrics

register = template.Library()

@register.filter
def get_performance_metric(performance_metrics, job_id):
    # Return the performance metric for the given job_id, or None if not found
    return performance_metrics.filter(job_id=job_id).first()
@register.filter
def get_productivity(productivity, job_id):
    return productivity[job_id -1]
@register.filter
def get_attente(attente_job, job_id):
    return attente_job[job_id -1]
@register.filter
def get_TFR(TFR, machine_id):
    return TFR[machine_id -1]
@register.filter
def get_TAR(TAR, machine_id):
    return TAR[machine_id -1]
