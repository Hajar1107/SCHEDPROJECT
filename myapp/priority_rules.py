from .models import Job, Machine, Problem, ProcessingTime


def FIFO(jobs):
    """
    FIFO (First In, First Out) priority rule.
    Args:
        jobs (QuerySet): Liste des jobs (QuerySet Django).
    Returns:
        list: Séquence triée des indices des jobs.
    """
    # Trier les jobs par `arrival_time` (temps d'arrivée).
    jobs = jobs.order_by('arrival_time')
    # Créer la séquence des jobs basée sur leur ordre d'arrivée.
    sequence = [job.id for job in jobs]
    return sequence


def LIFO(jobs):
    """
    LIFO (Last In, First Out) priority rule.
    Args:
        jobs (QuerySet): Liste des jobs (QuerySet Django).
    Returns:
        list: Séquence triée des indices des jobs.
    """
    # Trier les jobs par `arrival_time` dans l'ordre inverse.
    jobs = jobs.order_by('-arrival_time')
    # Créer la séquence des jobs basée sur leur ordre inverse d'arrivée.
    sequence = [job.id for job in jobs]
    return sequence


def SPT(jobs):
    """
    SPT (Shortest Processing Time) priority rule.
    Args:
        jobs (QuerySet): Liste des jobs (QuerySet Django).
    Returns:
        list: Séquence triée des indices des jobs.
    """
    # Calculer le temps de traitement total de chaque job sur toutes les machines
    jobs_with_total_processing = []
    for job in jobs:
        total_processing_time = sum(
            ProcessingTime.objects.filter(job=job).values_list('processing_time', flat=True)
        )
        jobs_with_total_processing.append((job.id, total_processing_time))

    # Trier les jobs par leur temps de traitement total (du plus court au plus long)
    sorted_jobs = sorted(jobs_with_total_processing, key=lambda x: x[1])
    sequence = [job[0] for job in sorted_jobs]  # Récupérer l'ID des jobs triés
    return sequence


def LPT(jobs):
    """
    LPT (Longest Processing Time) priority rule.
    Args:
        jobs (QuerySet): Liste des jobs (QuerySet Django).
    Returns:
        list: Séquence triée des indices des jobs.
    """
    # Utiliser SPT et inverser la séquence (du plus long au plus court)
    sequence = SPT(jobs)[::-1]
    return sequence


def EDD(jobs):
    """
    EDD (Earliest Due Date) priority rule.
    Args:
        jobs (QuerySet): Liste des jobs (QuerySet Django).
    Returns:
        list: Séquence triée des indices des jobs.
    """
    # Extract job IDs and their due dates
    jobs_with_due_dates = []
    for job in jobs:
        jobs_with_due_dates.append((job.id, job.due_date))  # (Job ID, Due Date)

    # Sort jobs by due date (ascending order)
    sorted_jobs = sorted(jobs_with_due_dates, key=lambda x: x[1])
    
    # Extract the sorted sequence of job IDs
    sequence = [job[0] for job in sorted_jobs]
    return sequence

def WDD(jobs):
    """
    WDD (Weighted Due Date) priority rule.
    Args:
        jobs (QuerySet): List of jobs (QuerySet Django).
    Returns:
        list: Sorted sequence of job IDs based on WDD.
    """
    # Extract job IDs, due dates, and weights
    jobs_with_wdd = []
    for job in jobs:
        #print(f"Job ID: {job.id}, Due Date: {job.due_date}, Weight: {job.weight}")
        wdd_value = job.due_date * job.weight  # Calculate WDD (due date * weight)
        jobs_with_wdd.append((job.id, wdd_value))  # (Job ID, WDD Value)

    # Sort jobs by WDD in descending order
    sorted_jobs = sorted(jobs_with_wdd, key=lambda x: x[1], reverse=True)

    # Extract the sorted sequence of job IDs
    sequence = [job[0] for job in sorted_jobs]
    return sequence



