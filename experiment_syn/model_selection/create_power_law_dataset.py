'''
This program creates (task, worker, label)-dataset according to power law.
There are m workers.
The number of times of labeling by each worker follows power law.
Each worker label each task according to his confusion matrix.
'''

import numpy as np


def create_data(n, K, proportion):
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


def create_crowd(m, K, N, proportion):
    '''
    :param m:           The number of workers
    :param K:           The number of classes
    :param N:           The maximum number of times of labeling by one worker
    :param proportion:  The proportion of each worker type, that is honest, spammer, and adversary
    :return worker:     List of workers = crowd. Each element of the list is a triple of
                        (worker-id, confusion matrix, number of labeling).
    We make m workers.
    There are m * proportion[0] honests.
    There are m * proportion[1] spammers.
    There are m * proportion[2] adversaries.
    '''
    worker = [[i, np.zeros((K, K)), 0] for i in np.arange(m)]
    np.random.shuffle(worker)
    i = 0
    for k in range(3):
        for j in range(i, i + int(m * proportion[k])):
            worker[j][1] = create_confusion_matrix(K, k)
        i += int(m * proportion[k])
    for j in range(i, m):
        worker[j][1] = create_confusion_matrix(K, 2)
    np.random.shuffle(worker)

    S = m / np.sum([1 / k for k in range(1, N + 1)])
    i = 0
    for k in range(1, N + 1):
        di = int(S / k)
        if di >= 1:
            for j in range(i, i + di):
                worker[j][2] = k
            i += di
        else:
            if i < m:
                worker[i][2] = k
            i += 1
    for j in range(i, m):
        worker[j][2] = 1
    return worker


import pandas as pd


def task_worker_label(m, K, task, true_label, maxN, proportion):
    worker = create_crowd(m, K, maxN, proportion)
    task_worker_class = np.array([], dtype=int).reshape(0, 3)
    n = task.shape[0]
    for index_j in range(m):
        j = worker[index_j][0]
        conf_mat = worker[index_j][1]
        num_label = worker[index_j][2]
        for _ in range(num_label):
            index_i = np.random.choice(n)
            i = task[index_i]
            true = true_label[index_i]
            k = np.random.choice(np.arange(K), p=conf_mat[true])
            task_worker_class = np.concatenate((task_worker_class, [[i, j, k]]))
    for index_i in range(n):
        i = task[index_i]
        one_worker = worker[np.random.choice(m)]
        j = one_worker[0]
        confusion_matrix = one_worker[1]
        true = true_label[index_i]
        k = np.random.choice(np.arange(K), p=confusion_matrix[true])
        task_worker_class = np.concatenate((task_worker_class, [[i, j, k]]))
    print(list(pd.DataFrame(worker)[2]))
    return task_worker_class
