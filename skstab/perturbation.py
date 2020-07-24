"""
skstab - Perturbation functions

@author Florent Forest, Alex Mourer
"""

import numpy as np


"""
Generic perturbations
"""


def subsample(x, f, return_indices=False):
    """Sample a fraction f of the data set without replacement"""
    idx = np.random.choice(x.shape[0], size=int(f * x.shape[0]), replace=False)
    if return_indices:
        return x[idx], idx
    else:
        return x[idx]


def bootstrap(x, return_indices=False):
    """Bootstrap the data set with replacement"""
    idx = np.random.choice(x.shape[0], size=x.shape[0], replace=True)
    if return_indices:
        return x[idx], idx
    else:
        return x[idx]


def uniform_additive_noise(x, eps):
    """Uniform additive noise of level eps"""
    noise = np.random.uniform(low=-eps, high=eps, size=x.shape)
    return x + noise


def gaussian_additive_noise(x, sigma):
    """Gaussian additive noise of standard deviation sigma"""
    noise = np.random.normal(0.0, sigma, size=x.shape)
    return x + noise


"""
Time series perturbations (univariate)
"""


def random_shift(x, alpha):
    """Random temporal shifting of a fraction alpha of the time series length"""
    shift = (x.shape[1] * np.random.uniform(low=-alpha, high=alpha, size=x.shape[0])).astype('int')
    x_shifted = np.zeros_like(x)
    # pad with first and last values
    for i in range(x.shape[0]):
        if shift[i] > 0:
            x_shifted[i, :] = np.pad(x[i, :-shift[i]], (shift[i], 0), mode='edge')
        else:
            x_shifted[i, :] = np.pad(x[i, -shift[i]:], (0, -shift[i]), mode='edge')
    return x_shifted


def random_offset(x, eps):
    """Random vertical offset"""
    offset = np.random.uniform(low=-eps, high=eps, size=x.shape[0])
    return x + offset[:, None]


def random_scale(x, eps):
    """Random vertical scaling"""
    scale = np.random.uniform(low=1.0 / (1.0 + eps), high=1.0 + eps, size=x.shape[0])
    return x * scale[:, None]


def random_warp(x, alpha, eps):
    """Random local warping of alpha of the time series length and intensity eps"""
    start = np.random.choice(x.shape[1], size=x.shape[0])  # random position in the time series
    end = start + 1 + (x.shape[1] * np.random.uniform(low=0, high=alpha, size=x.shape[0])).astype('int')  # end position to warp
    end = np.minimum(end, x.shape[1])  # clip end at end of time series
    warp = np.random.uniform(low=1.0 / (1.0 + eps), high=1.0 + eps, size=x.shape[0])  # warping level
    warped_end = start + (warp * (end - start)).astype('int')
    warped_end = np.minimum(warped_end, x.shape[1])  # clip warp end at end of time series
    x_warped = np.zeros_like(x)
    for i in range(x.shape[0]):
        segment = x[i, start[i]:end[i]]
        warped_segment = np.interp(np.linspace(0, 1, num=(warped_end[i] - start[i])), np.linspace(0, 1, num=segment.size), segment)
        x_warped[i, :start[i]] = x[i, :start[i]]
        x_warped[i, start[i]:warped_end[i]] = warped_segment
        if warped_end[i] < x.shape[1]:  # if the end of the time series was not reached
            if warp[i] >= 1.0:  # dilation: fill with end of original time series
                x_warped[i, warped_end[i]:] = x[i, end[i]:end[i] + x.shape[1] - warped_end[i]]
            else:  # reduction: end of original time series is not long enough, pad with last value
                x_warped[i, warped_end[i]:warped_end[i] + x.shape[1] - end[i]] = x[i, end[i]:]
                x_warped[i, warped_end[i] + x.shape[1] - end[i]:] = x[i, -1] # pad the rest with last value
    return x_warped
