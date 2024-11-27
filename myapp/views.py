from django.shortcuts import render, redirect
from .models import Problem, Machine, Job, ProcessingTime, StartingTime, CompletionTime, PerformanceMetrics, ProblemPerformanceMetrics
from .priority_rules import FIFO, LIFO, LPT, SPT, EDD, WDD
from .constraints import NO_WAIT , NO_IDLE , NO_CONSTRAINT #, BLOCKING, AVAILABILITY, SDST, SIST
from .ganttchart import GanttChartGenerator
from .performance_metrics import calculate_metrics
from .report_functions import TAR_TFR, attente, job_productivity, client_satisfaction


############################### PAGE 1 : HOMEPAGE ###############################
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')  # Rendre le template 'about.html'

def service(request):
    return render(request, 'service.html')

def why(request):
    return render(request, 'why.html')

def team(request):
    return render(request, 'team.html')

############################### PAGE 2 : CHOIX DU PROBLEME, n et m ###############################

def order_problem(request):
    if request.method == "POST":
        # Récupérer les informations du formulaire
        n_jobs = int(request.POST.get('n_jobs'))
        m_machines = int(request.POST.get('m_machines'))
        problem_type = request.POST.get('problem_type')

        # Créer le problème
        problem = Problem.objects.create(n_jobs=n_jobs, m_machines=m_machines, problem_type=problem_type)

        # Créer les jobs associés au problème
        for i in range(1, n_jobs + 1):
            Job.objects.create(name=f"Job_{i}", arrival_time=0, due_date=0, weight=1.0, problem=problem)  

        # Créer les machines associées au problème
        for i in range(1, m_machines + 1):
            Machine.objects.create(name=f"Machine_{i}", problem=problem)

        # Enregistrer l'ID du problème dans la session
        request.session['problem_id'] = problem.id

        if problem_type == 'FlowShop' :
            return redirect('order_problem_FS')
        else:
            return redirect('order_problem_JS')


    return render(request, 'order_problem.html')

############################## PAGE 3 : FLOWSHOP, CONTRAINTES , PRIORITY RULE ###############################

def order_problem_FS(request):
    # Récupérer l'ID du problème depuis la session
    problem_id = request.session.get('problem_id')
    problem = Problem.objects.get(id=problem_id)

    if request.method == "POST":
        # Récupérer les règles et contraintes du formulaire
        priority_rule = request.POST.get('priority_rule')
        constraint = request.POST.get('constraint')

        # Mettre à jour le problème
        problem.priority_rule = priority_rule
        problem.constraint = constraint
        problem.save()

        # Rediriger vers la vue P_Matrix
        return redirect('P_Matrix')

    return render(request, 'order_problem_FS.html', {
        'problem': problem,
    })

############################### PAGE 4 : ENTREE DE LA MATRICE P #############################

def P_Matrix(request):
    # Récupérer le problème à partir de la session
    problem_id = request.session.get('problem_id')
    problem = Problem.objects.get(id=problem_id)

    # Récupérer les jobs et les machines associés
    jobs = problem.job_set.all()
    machines = problem.machine_set.all()

    if request.method == "POST":
        # Mettre à jour les temps de traitement pour chaque combinaison job-machine
        for machine in machines:
            for job in jobs:
                processing_time_value = int(request.POST.get(f'processing_time_{machine.id}_{job.id}'))
                ProcessingTime.objects.update_or_create(
                    job=job,
                    machine=machine,
                    defaults={'processing_time': processing_time_value}
                )

        # Mettre à jour les temps d'arrivée et les délais de livraison pour chaque job
        for job in jobs:
            arrival_time_value = int(request.POST.get(f'arrival_time_J_{job.id}'))
            due_date_value = int(request.POST.get(f'due_date_J_{job.id}'))
            weight_value = float(request.POST.get(f'weight_J_{job.id}')) 
            job.arrival_time = arrival_time_value
            job.due_date = due_date_value
            job.weight = weight_value
            job.save()

        # Rediriger vers la page de traitement du problème (par exemple, `process_problem`)
        return redirect('process_problem')

    return render(request, 'P_Matrix.html', {
        'problem': problem,
        'jobs': jobs,
        'machines': machines,
    })

############################## PAGE 5 : RESULTAT D'ORDONNANCEMENT #####################################

def process_problem(request):
    # Retrieve the problem from the session
    problem_id = request.session.get('problem_id')
    problem = Problem.objects.get(id=problem_id)
    machines = problem.machine_set.all()
    jobs = problem.job_set.all()

    # Generate the sequence of jobs
    sequence = generate_sequence(problem)
    request.session['sequence'] = sequence


    # Evaluate constraints (output is already saved in the database)
    starting_times_matrix, completion_times_matrix = evaluate_constraints(problem_id, sequence)
    request.session['starting_times'] = starting_times_matrix
    request.session['completion_times'] = completion_times_matrix


    # Créer une liste de tuples pour les machines et leurs temps de départ et de fin
    machine_data = []

    for machine in machines:
        machine_starting_times = []
        machine_completion_times = []
        for job in jobs:
            starting_time = StartingTime.objects.get(job=job, machine=machine)
            completion_time = CompletionTime.objects.get(job=job, machine=machine)
            machine_starting_times.append(starting_time.ST)
            machine_completion_times.append(completion_time.CT)
        machine_data.append((machine, machine_starting_times, machine_completion_times))

    #Calculer les métriques de performance
    calculate_metrics(problem_id, sequence, completion_times_matrix)
    
    problem_performance_metrics = ProblemPerformanceMetrics.objects.filter(problem_id=problem_id).first()
    print("Cmax = ", problem_performance_metrics.Makespan)
    
    # Generate Gantt chart
    gantt_generator = GanttChartGenerator()
    chart_path = gantt_generator.generate_chart(
        sequence=sequence,
        machines=problem.machine_set.all(),
        start_times=starting_times_matrix,
        completion_times=completion_times_matrix
    )
    

    # Pass everything to the template
    return render(request, 'result_view.html', {
        'problem': problem,
        'sequence': sequence,
        'machines': machines,
        'jobs': jobs,
        'machine_data' : machine_data,
        'gantt_chart_path': chart_path,
        'problem_performance_metrics' : problem_performance_metrics,
    })

######################### PAGE 6 : RAPPORT DE MACHINES ##########################

def machine_report(request):
    problem_id = request.session.get('problem_id')  
    problem = Problem.objects.get(id = problem_id)
    machines = problem.machine_set.all()
    TFR, TAR, LOAD = TAR_TFR(problem_id)
    
    return render(request, 'machine_report.html', {
        'TAR' : TAR,
        'TFR' : TFR,
        'LOAD' : LOAD,
        'machines' : machines,
     })


########################### PAGE 6 : RAPPORT DE JOBS ##################################

def job_report(request):
    problem_id = request.session.get('problem_id')
    sequence = request.session.get('sequence')
    problem = Problem.objects.get(id=problem_id)
    jobs = problem.job_set.all()
    performance_metrics = PerformanceMetrics.objects.filter(problem_id=problem_id)
    jobs_on_time = client_satisfaction(problem_id)
    productivity = job_productivity(problem_id)
    attente_job = attente(problem_id)
    print("attente des job : ", attente_job)

    return render(request, 'job_report.html', {
        'performance_metrics' : performance_metrics,
        'jobs_on_time' : jobs_on_time,
        'productivity' : productivity,
        'attente_job' : attente_job,
        'jobs' : jobs,
    })



###########################  FONCTION QUI GENERE LA SEQUENCE SELON PRIORITY RULE ########################
def generate_sequence(problem):
    """
    Dirige vers la fonction associée à la règle de priorité choisie.
    Args:
        problem (Problem): Instance du problème.
    Returns:
        tuple: (starting_times, completion_times) calculés en fonction de la contrainte.
    """

    jobs = problem.job_set.all()

    priority_rule_dispatch = {
        "FIFO": FIFO,
        "LIFO": LIFO,
        "LPT": LPT,
        "SPT": SPT,
        "EDD": EDD,
        "WDD": WDD,
    }

    rule_function = priority_rule_dispatch.get(problem.priority_rule)
    if rule_function:
        return rule_function(jobs)
    else:
        raise ValueError(f"Unknown priority rule: {problem.priority_rule}")

###################### FONCTION QUI CALCULE LES DATES DE DEBUT ET DE FIN SELON CONSTRAINT ########################
def evaluate_constraints(problem_id , sequence):

    problem = Problem.objects.get(id=problem_id)

    constraints_dispatch = {
        "" : NO_CONSTRAINT,
        "NO WAIT" : NO_WAIT,
        "NO IDLE" : NO_IDLE,
        #"BLOCKING" : BLOCKING,
        #"AVAILABILITY" : AVAILABILITY,
        #"SDST" : SDST,
        #"SIST" : SIST,
    }

    constraint_function = constraints_dispatch.get(problem.constraint)
    if constraint_function:
        # Assuming NO_WAIT returns starting_times, completion_times
        return constraint_function(problem_id, sequence)
    else:
        raise ValueError(f"Unknown constraint: {problem.constraint}")




def optimal_solution(request):
    return render(request, 'optimal_solution.html')