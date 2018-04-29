import numpy as np

'''
My proposed data set
'''


def create_dataset(n, K, proportion):
    '''
    :param n:           The number of tasks
    :param K:           The number of classes
    :param proportion:  The proportion of each classes
    :return task_class: The list of task-class pairs
     Each element of task_class is a pair of task and class.
     We make n pairs.
     The number of each class k \in [K] is n * proportion[k].
    '''
    task_class = np.c_[np.arange(n), np.zeros(n, dtype=int)]
    i = 0
    np.random.shuffle(task_class)
    for k in range(0, K - 1):
        task_class[np.arange(i, i + int(n * proportion[k])), 1] = k
        i += int(n * proportion[k])
    task_class[np.arange(i, n), 1] = K - 1
    return task_class


def create_confusion_matrix(K, k):
    '''
    :param K:       The number of classes.
    :param k:       The type of worker. 0 is honest. 1 is spammer. 2 is adversary.
    :return mat:    Confusion matrix.
    Each row of confusion matrix is generated by the dirichlet distribution.
    We have to set a parameter of dirichlet distribution, alpha, appropriately.
    We choose parameter p as concentration parameter of dirichlet parameter.
    If k == 0, then alpha = (a * b, b, ..., b).
    If k == 1, then alpha = (b, ..., b).
    If k == 2, then c = 1 / a and alpha = (c * b, b, ..., b).
    '''
    mat = np.zeros((K, K))
    a = 10
    b = 10
    if k == 0:
        alpha = np.concatenate(([a * b], b * np.ones(K - 1)))
    elif k == 1:
        alpha = b * np.ones(K)
    else:
        c = 1 / a
        alpha = np.concatenate(([c * b], b * np.ones(K - 1)))
    for i in range(K):
        mat[i] = np.random.dirichlet(alpha)
        alpha = np.concatenate(([alpha[K - 1]], alpha[0:K - 1]))
    return mat


def create_crowd(m, K, proportion):
    '''
    :param m:           The number of workers
    :param K:           The number of classes
    :param proportion:  The proportion of each worker type, that is honest, spammer, and adversary
    :return worker:     List of workers = crowd. Each element of the list is a pair of worker and his confusion matrix.
    We make m workers.
    There are m * proportion[0] honests.
    There are m * proportion[1] spammers.
    There are m * proportion[2] adversaries.
    '''
    worker = [[i, np.zeros((K, K))] for i in np.arange(m)]
    np.random.shuffle(worker)
    i = 0
    for k in range(3):
        for j in range(i, i + int(m * proportion[k])):
            worker[j][1] = create_confusion_matrix(K, k)
        i += int(m * proportion[k])
    for j in range(i, m):
        worker[j][1] = create_confusion_matrix(K, 2)
    return worker


def labeling_by_crowd(m, K, task, true_class, worker, N):
    '''
    :param m:                   The number of workers.
    :param K:                   The number of classes.
    :param task:                List of tasks
    :param true_class:          List of true class of tasks.
    :param worker:              List of workers = crowd
    :param N:                   The number of querying for each task.
    :return task_worker_class:  List of triplets of task, worker, and class
    This function is the simulation of labeling process.
    We bring each task to crowd N times, then worker selected randomly from crowd labels this task.
    '''
    task_worker_class = np.array([], dtype=int).reshape(0, 3)
    for _ in range(N):
        for index in range(task.shape[0]):
            i = task[index]
            one_worker = worker[np.random.choice(m)]
            j = one_worker[0]
            confusion_matrix = one_worker[1]
            true = true_class[index]
            k = np.random.choice(np.arange(K), p=confusion_matrix[true])
            task_worker_class = np.concatenate((task_worker_class, [[i, j, k]]))
    return task_worker_class


'''
Data set of "A Minimax Optimal Algorithm for Crowdsourcing"
'''


def create_dataset_Bonald(n, t, alpha, theta, proportion):
    '''
    :param n:                   The number of workers.
    :param t:                   The number of tasks.
    :param alpha:               Rating rate.
    :param theta:               Reliability of each worker. theta[i] denotes a reliability of worker i.
    :param proportion:          Proportion of each class.
    :return task_worker_class:  List of triplets, (task, worker, class).
    This function is the simulation of labeling process given by Bonald and Combes in A Minimax Optimal Algorithm for
    Crowdsourcing".
    '''
    task_worker_class = np.array([], dtype=int).reshape(0, 3)
    G = np.hsplit(create_dataset(t, 2, proportion), [1])[1].ravel()
    for i in range(n):
        for s in range(t):
            c = np.random.choice(a=[G[s], 1 - G[s], 2], p=[alpha*(1+theta[i])/2, alpha*(1-theta[i])/2, 1-alpha])
            if c != 2:
                task_worker_class = np.concatenate((task_worker_class, [[s, i, c]]))
    return task_worker_class, G
