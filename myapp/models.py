from django.db import models


class Problem(models.Model):
    PROBLEM_TYPES = [
        ('FlowShop', 'FlowShop'),
        ('JobShop', 'JobShop'),
    ]

    PRIORITY_RULES = [
        ('FIFO', 'FIFO'),
        ('LIFO', 'LIFO'),
        ('LPT', 'LPT'),
        ('SPT', 'SPT'),
        ('EDD', 'EDD'),
        ('JOHNSON', 'JOHNSON'),
        ('CDS', 'CDS'),
    ]

    CONSTRAINTS = [
        ('NO IDLE', 'NO IDLE'),
        ('NO WAIT', 'NO WAIT'),
        ('BLOCKING', 'BLOCKING'),
        ('SDST', 'SDST'),
        ('SIST', 'SIST'),
        ('AVAILABILITY', 'AVAILABILITY'),
    ]
    n_jobs = models.IntegerField()
    m_machines = models.IntegerField()
    problem_type = models.CharField(max_length=20, choices=PROBLEM_TYPES)
    priority_rule = models.CharField(max_length=20, choices=PRIORITY_RULES, blank=True, null=True)
    constraint = models.CharField(max_length=20, choices=CONSTRAINTS, blank=True, null=True)
    
    def __str__(self):
        return f"Problem {self.id}"

# Modèle pour un Job
class Job(models.Model):
    name = models.CharField(max_length=100)  # Nom du job
    arrival_time = models.IntegerField()  # Temps d'arrivée du job
    due_date = models.IntegerField()  # Date limite du job
    weight = models.FloatField()  # Job's Weight
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)  # Lien vers un problème

    def __str__(self):
        return self.name

# Modèle pour une Machine
class Machine(models.Model):
    name = models.CharField(max_length=100)  # Nom de la machine
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)  # Lien vers un problème

    def __str__(self):
        return self.name

# Modèle pour la matrice de traitement (Processing Time Matrix)
class ProcessingTime(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, default=1)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)  # Lien vers un job
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)  # Lien vers une machine
    processing_time = models.IntegerField()  # Temps de traitement pour ce job sur cette machine

    class Meta:
        unique_together = ('job', 'machine')  # Chaque combinaison de job et machine doit être unique

    def __str__(self):
        return f"Processing Time for {self.job.name} on {self.machine.name}: {self.processing_time} units"

    
    def __str__(self):
        return f"{self.problem_type} - {self.n_jobs} Jobs, {self.m_machines} Machines"
    

class StartingTime(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, default=1)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    ST = models.IntegerField()

class CompletionTime(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, default=1)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    CT = models.IntegerField()

class PerformanceMetrics(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, default=1)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    T = models.IntegerField()
    E = models.IntegerField()
    FT = models.IntegerField()

class ProblemPerformanceMetrics(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, default=1)
    Makespan = models.IntegerField()
    TFT = models.IntegerField()
    TT = models.IntegerField()
    TE = models.IntegerField()
    TU = models.IntegerField()