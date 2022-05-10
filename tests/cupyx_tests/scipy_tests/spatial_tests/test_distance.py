import unittest

import numpy
import cupy
try:
    import scipy.spatial  # NOQA
    import scipy.spatial.distance  # NOQA
    scipy_available = True
except ImportError:
    scipy_available = False
import cupyx.scipy.spatial.distance  # NOQA
try:
    import pylibraft  # NOQA
    pylibraft_available = True
except ImportError:
    pylibraft_available = False
from cupy import testing


@testing.gpu
@testing.with_requires("scipy")
@testing.parameterize(*testing.product({
    'dtype': ['float32', 'float64'],
    'rows': [20, 100],
    'cols': [20, 100],
    'metric': ['euclidean', 'cityblock', 'canberra', 'chebyshev',
               'hamming', 'correlation', 'jensenshannon', 'russellrao',
               "minkowski"],
    'p': [2.0],
    'order': ["C", "F"]
}))
@unittest.skipUnless(scipy_available and pylibraft_available,
                     'requires scipy and pylibcugraph')
class TestCdist(unittest.TestCase):

    def _make_matrix(self, xp, dtype, order):
        shape = (self.rows, self.cols)
        return testing.shaped_random(shape, xp, dtype=dtype, scale=1, order=order)

    @testing.numpy_cupy_array_almost_equal(decimal=4, scipy_name='scp')
    def test_cdist_(self, xp, scp):

        a = self._make_matrix(xp, self.dtype, self.order)

        # RussellRao expects boolean arrays
        if self.metric == "russellrao":
            a[a < 0.5] = 0
            a[a >= 0.5] = 1

        # JensenShannon expects probability arrays
        elif self.metric == "jensenshannon":
            a_n = a
            if xp == cupy:
                a_n = a_n.get()

            # l1 normalization is different between cupy and numpy
            # so use numpy.
            norm = numpy.sum(a_n, axis=1)
            a = (a_n.T / norm).T
            if xp == cupy:
                a = cupy.asarray(a)

        if self.metric == 'minkowski':
            out = scp.spatial.distance.cdist(a, a, metric=self.metric, p=self.p).astype(self.dtype)
        else:
            out = scp.spatial.distance.cdist(a, a, metric=self.metric).astype(self.dtype)

        print(str(out.shape))
        return out


@testing.gpu
@testing.with_requires("scipy")
@testing.parameterize(*testing.product({
    'dtype': ['float32', 'float64'],
    'rows': [20, 100],
    'cols': [20, 100],
    'p': [2.0],
    'order': ["C", "F"]
}))
@unittest.skipUnless(scipy_available and pylibraft_available,
                     'requires scipy and pylibcugraph')
class TestDistanceMatrix(unittest.TestCase):

    def _make_matrix(self, xp, dtype, order):
        shape = (self.rows, self.cols)
        return testing.shaped_random(shape, xp, dtype=dtype, scale=1, order=order)

    @testing.numpy_cupy_array_almost_equal(decimal=4, scipy_name='scp')
    def test_distance_matrix_(self, xp, scp):

        a = self._make_matrix(xp, self.dtype, self.order)
        out = scp.spatial.distance_matrix(a, a, p=self.p).astype(self.dtype)
        return out

