import numpy as np
import pandas as pd

import pytest
from scipy.linalg import toeplitz

from sklearn.datasets import make_spd_matrix
from doubleml.datasets import make_plr_turrell2018


def _g(x):
    return np.power(np.sin(x), 2)


def _m(x, nu=0., gamma=1.):
    return 0.5 / np.pi * (np.sinh(gamma)) / (np.cosh(gamma) - np.cos(x - nu))


def _m2(x):
    return np.power(x, 2)


@pytest.fixture(scope='session',
                params=[(1000, 20)])
def generate_data_bivariate(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = np.array([0.5, 0.9])
    b = [1 / k for k in range(1, p + 1)]
    sigma = make_spd_matrix(p)

    # generating data
    x = np.random.multivariate_normal(np.zeros(p), sigma, size=[n, ])
    G = _g(np.dot(x, b))
    M0 = _m(np.dot(x, b))
    M1 = _m2(np.dot(x, b))
    D0 = M0 + np.random.standard_normal(size=[n, ])
    D1 = M1 + np.random.standard_normal(size=[n, ])
    y = theta[0] * D0 + theta[1] * D1 + G + np.random.standard_normal(size=[n, ])
    d = np.column_stack((D0, D1))
    column_names = [f'X{i + 1}' for i in np.arange(p)] + ['y'] + \
                   [f'd{i + 1}' for i in np.arange(2)]
    data = pd.DataFrame(np.column_stack((x, y, d)),
                        columns=column_names)

    return data


@pytest.fixture(scope='session',
                params=[(1000, 20)])
def generate_data_toeplitz(request, betamax=4, decay=0.99, threshold=0, noisevar=10):
    n_p = request.param
    np.random.seed(3141)
    # setting parameters
    n = n_p[0]
    p = n_p[1]

    beta = np.array([betamax * np.power(j + 1, -decay) for j in range(p)])
    beta[beta < threshold] = 0

    cols_treatment = [0, 4, 9]

    sigma = toeplitz([np.power(0.9, k) for k in range(p)])
    mu = np.zeros(p)

    # generating data
    x = np.random.multivariate_normal(mu, sigma, size=[n, ])
    y = np.dot(x, beta) + np.random.normal(loc=0.0, scale=np.sqrt(noisevar), size=[n, ])
    d = x[:, cols_treatment]
    x = np.delete(x, cols_treatment, axis=1)
    column_names = [f'X{i + 1}' for i in np.arange(x.shape[1])] + \
                   ['y'] + [f'd{i + 1}' for i in np.arange(len(cols_treatment))]
    data = pd.DataFrame(np.column_stack((x, y, d)),
                        columns=column_names)

    return data


@pytest.fixture(scope='session',
                params=[(500, 10),
                        (1000, 20),
                        (1000, 100)])
def generate_data1(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = 0.5

    # generating data
    data = make_plr_turrell2018(n, p, theta, return_type=pd.DataFrame)

    return data


@pytest.fixture(scope='session',
                params=[(500, 20)])
def generate_data2(request):
    n_p = request.param
    np.random.seed(1111)
    # setting parameters
    n = n_p[0]
    p = n_p[1]
    theta = 0.5

    # generating data
    data = make_plr_turrell2018(n, p, theta)

    return data
