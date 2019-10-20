import numpy as np
from implementation import *
from data_analysis import *
from plots import *

##### Cross validation #####

def cross_validation_lambda(y, tX, k_fold=4):
    seed = 1
    #lambdas = [0, 0.1, 0.15, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5]
    lambdas = np.logspace(-7,6,100)
    # split data in k fold
    k_indices = build_k_indices(y, k_fold, seed)
    # define lists to store the loss of training data and test data
    rmse_tr = []
    rmse_te = []
    # cross validation
    for lambda_ in lambdas:
        loss_tr = 0.0
        loss_te = 0.0
        for k in range(k_fold):
            l_tr, l_te = cross_validation(y, tX, k_indices, k, lambda_)
            loss_tr = loss_tr + l_tr
            loss_te = loss_te + l_te
        loss_tr = loss_tr/(k_fold)
        loss_te = loss_te/(k_fold)
        rmse_tr.append(loss_tr)
        rmse_te.append(loss_te)
    optimal_lambda = lambdas[np.argmin(rmse_te)]
    return optimal_lambda

def cross_validation_degree(y, tX, feat_ind, expansion_degrees, maxDeg=3, k_fold=4):
    """
    feat_ind : index of the feature over which cross validation is done to find the optimal_degree
    expansion_degrees : indicates to what order should the other features be during the cross validation.
    """
    seed = 1
    degrees = np.arange(1,maxDeg+1)
    k_indices = build_k_indices(y, k_fold, seed)  # split data in k fold
    rmse_tr = []
    rmse_te = []
    # cross validation
    for degree in degrees:
        loss_tr = 0.0
        loss_te = 0.0
        expansion_degrees[feat_ind] = degree # change degree of feature at index 'feat_ind'
        tX = build_multi_poly(tX, expansion_degrees)
        for k in range(k_fold):
            print('--feat_ind', feat_ind, ', degree', degree, ', fold', k)
            l_tr, l_te = cross_validation(y, tX, k_indices, k)
            loss_tr = loss_tr + l_tr
            loss_te = loss_te + l_te
        loss_tr = loss_tr/(k_fold)
        loss_te = loss_te/(k_fold)
        rmse_tr.append(loss_tr)
        rmse_te.append(loss_te)
  
    optimal_degree = np.argmin(losses_te)+1;
    return optimal_degree

def cross_validation(y, tx, k_indices, k,init_w0,lambda_=0.15,gamma=0.003,max_iters=15):
    degree = 3
    # get k'th subgroup in test, others in train
    te_indices = k_indices[k]
    tr_indices = k_indices[~(np.arange(k_indices.shape[0]) == k)]
    tr_indices = tr_indices.reshape(-1)
    tr_indices = tr_indices.astype(np.int64)
    tx_tr = tx[tr_indices]
    y_tr = y[tr_indices]
    tx_te = tx[te_indices]
    y_te = y[te_indices]
    tx_tr = build_poly(tx_tr, degree)
    tx_te = build_poly(tx_te, degree)
    
    #weight, loss_tr = ridge_regression(y_tr, tx_tr, lambda_)     # ridge regression
    weight, loss_tr = logistic_regression(y0_tr, tX0_tr, init_w0, max_iters, gamma)
    # calculate the loss for train and test data
    rmse_tr = np.sqrt(2 * loss_tr)
    rmse_te = np.sqrt(2 * compute_loss(y_te, tx_te, weight))
    return rmse_tr, rmse_te

def build_k_indices(y, k_fold, seed):
    # build k indices for k-fold 
    num_row = y.shape[0]
    interval = int(num_row / k_fold)
    np.random.seed(seed)
    indices = np.random.permutation(num_row)
    k_indices = [indices[k * interval: (k + 1) * interval]
                 for k in range(k_fold)]
    return np.array(k_indices)

def cross_validation_degree_logistic(y0_tr,tX0_tr,y0_te,tX0_te,init_w0, max_iters, gamma):
    deg0 = np.ones(tX0_tr.shape[1],np.int64)
    degrees=range(1,4)
    for feat_ind in range(len(deg0)):
        grades=[]
        for degree_ in degrees:
            deg0[feat_ind]=degree_
            tX0_te=build_multi_poly(tX0_te,deg0)
            tX0_tr=build_multi_poly(tX0_tr,deg0)
            init_w0, _ = least_squares(y0_tr, tX0_tr)
            w0, loss0 = logistic_regression(y0_tr, tX0_tr, init_w0, max_iters, gamma)

            y0_pred = predict_labels(w0, tX0_te)
            res0 = np.where(y0_te[:,] == y0_pred[:,], 1, 0)
            grades.append(np.mean(res0))
            
        deg0[feat_ind]= degrees[np.argmax(grades)]
    return deg0

