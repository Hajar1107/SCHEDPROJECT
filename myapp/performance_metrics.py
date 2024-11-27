from django.db import transaction
from myapp.models import Job, Machine, Problem , PerformanceMetrics, ProblemPerformanceMetrics

def calculate_metrics(problem_id, sequence, completion_times_matrix):

    problem = Problem.objects.get(id=problem_id)
    machines = problem.machine_set.all()
    jobs = problem.job_set.all()
    n_jobs = len(sequence)
    m_machines = machines.count()

    due_dates = {job.id: job.due_date for job in jobs}
    arrival_times = {job.id: job.arrival_time for job in jobs}
    
    T = []  #  Tardiness
    E = []  #  Earliness
    FT = []  #  Flow Time
    TT = 0
    TE = 0
    TU = 0
    TFT = 0

    for j in range(len(sequence)):
        job_id = sequence[j]
        FTj = completion_times_matrix[-1][j] - arrival_times[job_id]
        FT.append(FTj)
        TFT += FTj
        Tj = max(completion_times_matrix[-1][j] - due_dates[job_id], 0)
        T.append(Tj)
        TT += Tj
        Ej = max(due_dates[job_id] - completion_times_matrix[-1][j], 0)
        E.append(Ej)
        TE += Ej
        if (Tj!=0): #Calcul du nombre de jobs en retard
            TU = TU + 1

    for j, job_id in enumerate(sequence):
        PerformanceMetrics.objects.create(
            problem = problem ,
            job_id = job_id ,
            T = T[j],
            E = E[j],
            FT = FT[j] )
    ProblemPerformanceMetrics.objects.create(
        problem = problem ,
        Makespan = max(completion_times_matrix[-1]),
        TT = TT,
        TE = TE,
        TU = TU,
        TFT = TFT
            ) 