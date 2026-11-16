def proxima_permutacao(a):
    n = len(a)

    i = n - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i < 0:
        return False

    j = n - 1
    while a[j] <= a[i]:
        j -= 1
    a[i], a[j] = a[j], a[i]

    esq, dir = i + 1, n - 1
    while esq < dir:
        a[esq], a[dir] = a[dir], a[esq]
        esq += 1
        dir -= 1
    return True


def valida(p, n):
    d1 = [False] * (2 * n - 1)  
    d2 = [False] * (2 * n - 1)  
    ok = True
    for i in range(n):
        a = i + p[i]
        b = i - p[i] + n - 1
        if d1[a] or d2[b]:
            ok = False
        d1[a] = True
        d2[b] = True
    return ok


def forca_bruta(n, pi, modo):
    idx = list(range(n))  
    p = [0] * n
    total = 0
    testadas = 0

    while True:
        for i in range(n):
            p[i] = pi[idx[i]]
        testadas += 1

        if valida(p, n):
            if modo == "primeira":
                return p, testadas
            total += 1

        if not proxima_permutacao(idx):
            break

    if modo == "primeira":
        return None, testadas
    return total, testadas
