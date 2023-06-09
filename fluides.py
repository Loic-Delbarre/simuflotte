import numpy as np
import scipy.sparse as sc
import scipy.sparse.linalg

g = 9.81
rho = 1000


def getCoeff(num_left, num_right, num_down, num_up, num_cent, type_cent, cl_cent):
    if type_cent == 1:
        a = np.mat([[1], [1], [1], [1], [-4]])
        j = np.mat([[num_left], [num_right], [num_down], [num_up], [num_cent]])
        b = 0
        return j, a, b
    if type_cent == 2:
        a = np.array([1])
        j = np.array([num_cent])
        b = cl_cent
        return j, a, b
    return 0


def laplace(dom, cl, num):
    ndata = 0
    for line in dom:
        for element in line:
            if 1 == element:
                ndata += 5
            elif 2 == element:
                ndata += 1  # ndata=number of data in the new matrix
    data, row, col = np.empty(ndata), np.empty(ndata), np.empty(ndata)
    btot = np.empty(int(np.max(num)))  # np.empty(((dom.shape[0] - 2) * (dom.shape[1] - 2)))
    index = 0  # index of data
    bindex = 0  # actual line index of b and A
    for x in range(1, dom.shape[0] - 1):  # skip  side bc =0
        for y in range(1, dom.shape[1] - 1):
            if 0 == dom[x, y]:  # to 0 in responses and skip expeption
                continue
            tcol, tdata, b = getCoeff(num[x - 1][y], num[x + 1][y], num[x][y - 1], num[x][y + 1], num[x][y], dom[x][y],
                                      cl[x][y])
            btot[bindex] = b
            for i in range(tdata.shape[0]):
                data[index] = tdata[i]
                row[index] = bindex  # chaque nouvelle ligne correspondante a un getCoeff = ligne pour b -> bindex
                col[index] = tcol[i] - 1
                index += 1
            bindex += 1
    maxsize = int(np.max(num))
    A = sc.csc_matrix((data, (row, col)), shape=(maxsize, maxsize))
    X = sc.linalg.spsolve(A, btot)
    psi = np.zeros_like(dom)
    for i in range(num.shape[0]):
        for j in range(num.shape[1]):
            if dom[i][j] != 0:
                psi[i][j] = X[num[i][j] - 1]
    return psi


def deriv(f_left, f_c, f_right, type_left, type_c, type_right, h):
    v = 0
    if type_c == 0:
        return 0
    if type_left != 0 and type_right != 0:
        denominator = 2 * h
        v = (f_right - f_left) / denominator
    elif type_left != 0 and type_right == 0:
        denominator = h
        v = (f_c - f_left) / denominator
    elif type_left == 0 and type_right != 0:
        denominator = h
        v = (f_right - f_c) / denominator
    return v


def circu(u, v, x, y):
    c = 0
    for i in range(x.shape[0] - 1):
        if x[i] == x[i + 1]:
            c += (y[i + 1] - y[i]) * (v[i + 1] + v[i]) / 2
        if y[i] == y[i + 1]:
            c += (x[i + 1] - x[i]) * (u[i + 1] + u[i]) / 2
    return c


def force(p, x, y):
    fx = fy = 0
    for i in range(x.shape[0] - 1):
        if x[i] == x[i + 1]:
            fx += ((p[i] + p[i + 1]) / 2) * (y[i + 1] - y[i])
        if y[i] == y[i + 1]:
            fy -= ((p[i] + p[i + 1]) / 2) * (x[i + 1] - x[i])
    return fx, fy


def velocity(dom, psi, h):
    u = np.zeros_like(psi)
    v = np.zeros_like(psi)
    for i in range(psi.shape[0]):
        for j in range(psi.shape[1]):
            if 0 != dom[i][j]:
                v[i][j] = -deriv(psi[i][j - 1], psi[i][j], psi[i][j + 1], dom[i][j - 1], dom[i][j], dom[i][j + 1], h)
                u[i][j] = deriv(psi[i - 1][j], psi[i][j], psi[i + 1][j], dom[i - 1][j], dom[i][j], dom[i + 1][j], h)
    return u, v


def pressure(u, v):
    U = v ** 2 + u ** 2
    return -rho * U / 2
