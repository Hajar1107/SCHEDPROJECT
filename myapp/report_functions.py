from myapp.models import Job, Machine, ProcessingTime, Problem, PerformanceMetrics, ProblemPerformanceMetrics, StartingTime, CompletionTime

################## Calcul du temps d'arret/fonctionnement réel   et  EQUILIBRAGE DE LA CHARGE  #############

def TAR_TFR(problem_id):
    problem = Problem.objects.get(id=problem_id)
    machines = Machine.objects.filter(problem_id=problem_id).order_by('id')
    jobs = Job.objects.filter(problem_id=problem_id)
    Global_Performance = ProblemPerformanceMetrics.objects.get(problem=problem)
    Cmax = Global_Performance.Makespan

    # Dictionary for processing times
    processing_times = {
        (pt.job.id, pt.machine.id): pt.processing_time 
        for pt in ProcessingTime.objects.filter(job__problem_id=problem_id)
    }

    TFR = [0] * problem.m_machines  # Total Functioning Rate for each machine
    TAR = [0] * problem.m_machines  # Total Idle Rate for each machine
    S = 0

    for i, machine in enumerate(machines):  # Fix: Use enumerate
        for job in jobs:
            S += processing_times.get((job.id, machine.id), 0)  # Avoid KeyError
        TFR[i] = (S / Cmax) * 100  # Active time as a percentage
        TAR[i] = 100 - TFR[i]  # Idle time as a percentage
        S = 0  # Reset S for the next machine

    load = max(TFR) - min(TFR)  # Load balancing metric

    return TFR, TAR, load


################## POURCENTAGE DES JOBS FINIS DANS LES DELAIS REQUIS #######################

def client_satisfaction(problem_id):
    problem = Problem.objects.get(id=problem_id)
    Global_Performance = ProblemPerformanceMetrics.objects.get(problem=problem)

    TU = Global_Performance.TU  # Total Unmet Jobs
    jobs_on_time = problem.n_jobs - TU  # Jobs finished on time
    percentage_on_time = (jobs_on_time / problem.n_jobs) * 100

    return percentage_on_time


################## PRODUCTIVITE PAR JOB ##############################

def job_productivity(problem_id):
    problem = Problem.objects.get(id=problem_id)
    jobs = Job.objects.filter(problem_id=problem_id)
    productivity_per_job = []

    for job in jobs:
        total_processing_time = sum(
            ProcessingTime.objects.filter(job=job).values_list('processing_time', flat=True)
        )
        flow_time_job = PerformanceMetrics.objects.filter(job=job).values_list('FT', flat=True).first()  # Use `.first()` to get the scalar
        if flow_time_job:  # Avoid division by zero or None
            productivity = (total_processing_time / flow_time_job)*100
        else:
            productivity = 0
        productivity_per_job.append(productivity)

    return productivity_per_job


######################### Temps d'attente des jobs #####################

def attente(problem_id):
    # Fetch the problem and related data
    problem = Problem.objects.get(id=problem_id)
    jobs = Job.objects.filter(problem_id=problem_id).order_by('id')

    # Fetch starting and completion times
    starting_times = {
        (pt.job.id, pt.machine.id): pt.ST for pt in StartingTime.objects.filter(job__problem_id=problem_id)
    }
    completion_times = {
        (pt.job.id, pt.machine.id): pt.CT for pt in CompletionTime.objects.filter(job__problem_id=problem_id)
    }

    # Print starting_times and completion_times to verify data
    print("Starting Times: ", starting_times)
    print("Completion Times: ", completion_times)

    # Calculate waiting times
    attente = []
    for j in range(len(jobs)):
        job_id = jobs[j].id  # Use the job's actual ID from the Job object
        print(f"Calculating for Job ID: {job_id}")
        
        attente_job = 0  # Reset for each job
        for i in range(1, problem.m_machines):  # Start from the second machine
            try:
                # Adjust indexing to ensure it's consistent with your database records
                st_key = (job_id, i + 1)  # Starting time key
                ct_key = (job_id, i)      # Completion time key
                
                # Check if keys exist in the dictionaries
                if st_key in starting_times and ct_key in completion_times:
                    wait_time = starting_times[st_key] - completion_times[ct_key]
                    print(f"Machine {i}, Job {job_id} - Wait Time: {wait_time}")
                    attente_job += max(wait_time, 0)  # Avoid negative wait times
                else:
                    print(f"Missing data for Job {job_id}, Machine {i}")
            except KeyError as e:
                print(f"KeyError: {e} - missing data for Job {job_id}, Machine {i}")
        
        print(f"Total Waiting Time for Job {job_id}: {attente_job}")
        attente.append(attente_job)

    return attente



