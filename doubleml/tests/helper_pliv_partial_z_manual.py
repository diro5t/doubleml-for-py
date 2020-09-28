import numpy as np

from doubleml.tests.helper_boot import boot_manual


def fit_nuisance_pliv_partial_z(Y, X, D, Z, ml_r, smpls):
    XZ = np.hstack((X, Z))
    r_hat = []
    for idx, (train_index, test_index) in enumerate(smpls):
        r_hat.append(ml_r.fit(XZ[train_index], D[train_index]).predict(XZ[test_index]))
    
    return r_hat


def pliv_partial_z_dml1(Y, X, D, Z, r_hat, smpls, score):
    thetas = np.zeros(len(smpls))
    n_obs = len(Y)
    
    for idx, (train_index, test_index) in enumerate(smpls):
        thetas[idx] = pliv_partial_z_orth(r_hat[idx], Y[test_index], D[test_index], score)
    theta_hat = np.mean(thetas)
    
    ses = np.zeros(len(smpls))
    for idx, (train_index, test_index) in enumerate(smpls):
        ses[idx] = var_pliv_partial_z(theta_hat,
                                       r_hat[idx], Y[test_index], D[test_index],
                                       score, n_obs)
    se = np.sqrt(np.mean(ses))
    
    return theta_hat, se


def pliv_partial_z_dml2(Y, X, D, Z, r_hat, smpls, score):
    n_obs = len(Y)
    r_hat_array = np.zeros_like(D)
    for idx, (train_index, test_index) in enumerate(smpls):
        r_hat_array[test_index] = r_hat[idx]
    theta_hat = pliv_partial_z_orth(r_hat_array, Y, D, score)
    se = np.sqrt(var_pliv_partial_z(theta_hat, r_hat_array, Y, D, score, n_obs))
    
    return theta_hat, se


def var_pliv_partial_z(theta, r_hat, y, d, score, n_obs):
    if score == 'partialling out':
        var = 1/n_obs * 1/np.power(np.mean(np.multiply(r_hat, d)), 2) * \
              np.mean(np.power(np.multiply(y - d*theta, r_hat), 2))
    else:
        raise ValueError('invalid score')
    
    return var


def pliv_partial_z_orth(r_hat, y, d, score):
    if score == 'partialling out':
        res = np.mean(np.multiply(r_hat, y))/np.mean(np.multiply(r_hat, d))
    else:
      raise ValueError('invalid score')
    
    return res


def boot_pliv_partial_z(theta, Y, D, Z, r_hat, smpls, score, se, bootstrap, n_rep, dml_procedure):
    r_hat_array = np.zeros_like(D)
    n_folds = len(smpls)
    J = np.zeros(n_folds)
    for idx, (train_index, test_index) in enumerate(smpls):
        r_hat_array[test_index] = r_hat[idx]
        if dml_procedure == 'dml1':
            if score == 'partialling out':
                J[idx] = np.mean(-np.multiply(r_hat_array[test_index], D[test_index]))

    if dml_procedure == 'dml2':
        if score == 'partialling out':
            J = np.mean(-np.multiply(r_hat_array, D))

    if score == 'partialling out':
        psi = np.multiply(Y - D*theta, r_hat_array)
    else:
        raise ValueError('invalid score')
    
    boot_theta = boot_manual(psi, J, smpls, se, bootstrap, n_rep, dml_procedure)

    return boot_theta