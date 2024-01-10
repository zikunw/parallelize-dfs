import multiprocessing as mp

def f(x):
    return x*x

if __name__ == '__main__':
    p = mp.Pool(5)
    print(p.map(f, [1, 2, 3]))
    p.terminate()
    p.terminate()