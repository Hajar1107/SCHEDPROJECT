from django.db import transaction
from myapp.models import Job, Machine, ProcessingTime, StartingTime, CompletionTime, Problem

@transaction.atomic
def NO_CONSTRAINT(problem_id, sequence):
    """
    Ordonnancement sans contrainte.
    :param problem_id: ID du problème.
    :param sequence: Séquence des jobs.
    """
    problem = Problem.objects.get(id=problem_id)
    # Clear existing StartingTime and CompletionTime for the problem
    StartingTime.objects.filter(job__problem_id=problem_id).delete()
    CompletionTime.objects.filter(job__problem_id=problem_id).delete()

    # Retrieve the machines and jobs
    machines = Machine.objects.filter(problem_id=problem_id).order_by('id')
    jobs = Job.objects.filter(problem_id=problem_id)
    m_machines = machines.count()
    n_jobs = len(sequence)

    # Fetch processing times and release times
    processing_times = {
        (pt.job.id, pt.machine.id): pt.processing_time for pt in ProcessingTime.objects.filter(job__problem_id=problem_id)
    }
    arrival_times = {job.id: job.arrival_time for job in jobs}

    # Initialize the starting and completion times matrices
    S = [[0] * n_jobs for _ in range(m_machines)]  # Starting times
    C = [[0] * n_jobs for _ in range(m_machines)]  # Completion times

    # First job on the first machine
    first_job = sequence[0]
    S[0][0] = arrival_times[first_job]
    C[0][0] = S[0][0] + processing_times[(first_job, machines[0].id)]

    # Calcul des dates pour la première machine pour tous les jobs
    for j in range(1, n_jobs):
        job_id = sequence[j]
        S[0][j] = max(C[0][j-1], arrival_times[job_id] )
        C[0][j] = S[0][j] + processing_times[(job_id, machines[0].id)]

    # Calcul des dates pour les autres machines
    for i in range(1, m_machines):
        S[i][0] = max(C[i-1][0], arrival_times[first_job])
        C[i][0] = S[i][0] + processing_times[(first_job, machines[i].id)]
        for j in range(1, n_jobs):
            job_id = sequence[j]
            S[i][j] = max(C[i][j-1], C[i-1][j])
            C[i][j] = S[i][j] + processing_times[(job_id, machines[i].id)]

    for j, job_id in enumerate(sequence):
        for i, machine in enumerate(machines):
            StartingTime.objects.create(
                problem = problem,
                job_id=job_id,
                machine=machine,
                ST=S[i][j]
            )
            CompletionTime.objects.create(
                problem = problem,
                job_id=job_id,
                machine=machine,
                CT=C[i][j]
            )
    return S, C

@transaction.atomic
def NO_WAIT(problem_id, sequence):
    """
    Implements the NO_WAIT constraint as per the Python `order` function.

    Args:
        problem_id (int): ID of the current problem.
        sequence (list): List of job IDs in the desired sequence.

    Returns:
        starting_times (list): Starting times matrix.
        completion_times (list): Completion times matrix.
    """
    problem = Problem.objects.get(id=problem_id)
    # Clear existing StartingTime and CompletionTime for the problem
    StartingTime.objects.filter(job__problem_id=problem_id).delete()
    CompletionTime.objects.filter(job__problem_id=problem_id).delete()

    # Retrieve the machines and jobs
    machines = Machine.objects.filter(problem_id=problem_id).order_by('id')
    jobs = Job.objects.filter(problem_id=problem_id)
    n_machines = machines.count()
    n_jobs = len(sequence)

    # Fetch processing times and release times
    processing_times = {
        (pt.job.id, pt.machine.id): pt.processing_time for pt in ProcessingTime.objects.filter(job__problem_id=problem_id)
    }
    arrival_times = {job.id: job.arrival_time for job in jobs}

    # Initialize the starting and completion times matrices
    S = [[0] * n_jobs for _ in range(n_machines)]  # Starting times
    C = [[0] * n_jobs for _ in range(n_machines)]  # Completion times

    # First job on the first machine
    first_job = sequence[0]
    S[0][0] = arrival_times[first_job]
    C[0][0] = S[0][0] + processing_times[(first_job, machines[0].id)]

    # First job on subsequent machines
    for i in range(1, n_machines):
        S[i][0] = C[i - 1][0]
        C[i][0] = S[i][0] + processing_times[(first_job, machines[i].id)]

    # Remaining jobs
    for j in range(1, n_jobs):
        job_id = sequence[j]
        for i in range(n_machines):
            if i == 0:  # First machine
                C[i][j] = max(
                    C[i + 1][j - 1],  # Completion on the next machine of the previous job
                    C[i][j - 1] + processing_times[(job_id, machines[i].id)],  # Completion on the same machine
                    arrival_times[job_id] + processing_times[(job_id, machines[i].id)]  # Release time
                )
                S[i][j] = C[i][j] - processing_times[(job_id, machines[i].id)]
            elif i == n_machines - 1:  # Last machine
                S[i][j] = max(C[i - 1][j], C[i][j - 1])
                C[i][j] = S[i][j] + processing_times[(job_id, machines[i].id)]
            else:  # Intermediate machines
                C[i][j] = max(
                    C[i + 1][j - 1],  # Completion on the next machine of the previous job
                    C[i][j - 1] + processing_times[(job_id, machines[i].id)],  # Completion on the same machine
                    C[i - 1][j] + processing_times[(job_id, machines[i].id)]  # Completion on the previous machine
                )
                S[i][j] = C[i][j] - processing_times[(job_id, machines[i].id)]

            # Adjust earlier machines
            for k in range(i - 1, -1, -1):
                C[k][j] = S[k + 1][j]
                S[k][j] = C[k][j] - processing_times[(job_id, machines[k].id)]

    # Save starting and completion times in the database
    for j, job_id in enumerate(sequence):
        for i, machine in enumerate(machines):
            StartingTime.objects.create(
                problem = problem ,
                job_id=job_id,
                machine=machine,
                ST=S[i][j]
            )
            CompletionTime.objects.create(
                problem = problem ,
                job_id=job_id,
                machine=machine,
                CT=C[i][j]
            )

    return S, C


@transaction.atomic
def NO_IDLE(problem_id, sequence):
    """
    Implements the NO_IDLE constraint for a FlowShop problem.
    
    Args:
        problem_id (int): ID of the current problem.
        sequence (list): List of job IDs in the desired sequence.
    
    Returns:
        starting_times (list): Starting times matrix.
        completion_times (list): Completion times matrix.
    """
    problem = Problem.objects.get(id=problem_id)
    # Clear existing StartingTime and CompletionTime for the problem
    StartingTime.objects.filter(job__problem_id=problem_id).delete()
    CompletionTime.objects.filter(job__problem_id=problem_id).delete()

    # Retrieve the machines and jobs
    machines = Machine.objects.filter(problem_id=problem_id).order_by('id')
    jobs = Job.objects.filter(problem_id=problem_id)
    n_machines = machines.count()
    n_jobs = len(sequence)

    # Fetch processing times and arrival times
    processing_times = {
        (pt.job.id, pt.machine.id): pt.processing_time for pt in ProcessingTime.objects.filter(job__problem_id=problem_id)
    }

    # Map job sequence to zero-based indices for easier matrix operations
    job_sequence = [job_id - 1 for job_id in sequence]

    # Initialize arrays for start and completion times
    S = [[0] * n_jobs for _ in range(n_machines)]  # Starting times
    C = [[0] * n_jobs for _ in range(n_machines)]  # Completion times

    # Schedule jobs for the first machine
    current_time = 0
    for j in range(n_jobs):
        job_id = sequence[j]
        S[0][j] = current_time
        C[0][j] = current_time + processing_times[(job_id, machines[0].id)]
        current_time = C[0][j]

    # Schedule jobs for subsequent machines
    for i in range(1, n_machines):
        # Schedule the last job first
        j = n_jobs - 1
        job_id = sequence[j]
        S[i][j] = C[i - 1][j]
        C[i][j] = S[i][j] + processing_times[(job_id, machines[i].id)]

        # Schedule the remaining jobs backward
        for j in range(n_jobs - 2, -1, -1):
            job_id = sequence[j]
            earliest_start = C[i - 1][j]
            latest_completion = S[i][j + 1]

            # Calculate the initial start time
            S[i][j] = latest_completion - processing_times[(job_id, machines[i].id)]

            # Adjust if start time is less than the completion time of the previous machine
            if S[i][j] < earliest_start:
                shift = earliest_start - S[i][j]
                for k in range(j, n_jobs):
                    S[i][k] += shift
                    next_job_id = sequence[k]
                    C[i][k] = S[i][k] + processing_times[(next_job_id, machines[i].id)]
            else:
                C[i][j] = S[i][j] + processing_times[(job_id, machines[i].id)]

    # **DEBUGGING**: Print the matrices after the calculations
    #print("Starting Times Matrix:", S)
    #print("Completion Times Matrix:", C)

    # Save starting and completion times in the database
    for j, job_id in enumerate(sequence):
        for i, machine in enumerate(machines):
            StartingTime.objects.create(
                problem = problem ,
                job_id=job_id,
                machine=machine,
                ST=S[i][j]
            )
            CompletionTime.objects.create(
                problem = problem,
                job_id=job_id,
                machine=machine,
                CT=C[i][j]
            )

    return S, C




