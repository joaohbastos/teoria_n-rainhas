def backtracking(n, pi, modo):
    col = [False] * n         
    d1 = [False] * (2 * n - 1)  
    d2 = [False] * (2 * n - 1)   
    p = [0] * n
    total = 0
    nos = 0

    def coloca(i):
        nonlocal total, nos
        nos += 1

        if i == n:  
            if modo == "primeira":
                return True
            total += 1
            return False

        for j in range(n):
            c = pi[j]
            a = i + c
            b = i - c + n - 1
            if not col[c] and not d1[a] and not d2[b]:
                col[c] = d1[a] = d2[b] = True     
                p[i] = c
                if coloca(i + 1):
                    return True
                col[c] = d1[a] = d2[b] = False   
        return False

    achou = coloca(0)

    if modo == "primeira":
        return (p if achou else None), nos
    return total, nos
