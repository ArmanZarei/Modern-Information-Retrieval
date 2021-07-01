import numpy as np
import pandas as pd


def estimate(M, k, learning_rate, steps):
    observed_mask = (~M.isna()).to_numpy()
    train_mask = np.copy(observed_mask)
    train_mask[:M.shape[0]//2, :M.shape[1]//2] = 0
    test_mask = observed_mask ^ train_mask
    
    M.fillna(0, inplace=True)
    M = M.to_numpy()
    
    u, s, v = np.linalg.svd(M)
    s = np.diag(s)
    P = u[:, :k] @ s[:k, :k]
    Q = v[:k, :]

    for i in range(steps):
        P, Q = P - 2*learning_rate*(train_mask*(M - P@Q)) @ Q.T, Q - 2*learning_rate*(P.T @ ((M - P@Q)*train_mask))
        
    estimation = P@Q
    train_err = (train_mask * (M - P@Q)**2).sum()
    test_err = (test_mask * (M - P@Q)**2).sum()
    
    return estimation, train_err, test_err 

            
if __name__ == '__main__':
    estimation, train_error, test_error = estimate(pd.read_csv("../data.csv"), 2, 0.00001, 20)
    print("Train Error: %f" % train_error)
    print("Test Error: %f" % test_error)
