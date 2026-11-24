# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
import numpy as np
import pytest

from flow.network import Network


def make_net(edges, A, B, P=None, n=None, capacity=None):
    tail = np.array([e[0] for e in edges])
    head = np.array([e[1] for e in edges])
    n = n or int(max(tail.max(), head.max()) + 1)
    P = np.ones(len(edges)) if P is None else np.asarray(P, dtype=float)
    return Network(n_nodes=n, tail=tail, head=head, A=np.asarray(A, float), B=np.asarray(B, float), P=P, capacity=capacity)


@pytest.fixture
def pigou():
    """Two parallel routes 0->1 (via nodes 2 and 3 to avoid parallel links): t1 = 1, t2 = x."""
    return make_net([(0, 2), (2, 1), (0, 3), (3, 1)], A=[1, 0, 0, 0], B=[0, 0, 1, 0])
