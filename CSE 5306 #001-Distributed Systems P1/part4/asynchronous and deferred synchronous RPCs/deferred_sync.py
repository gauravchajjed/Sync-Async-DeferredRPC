from client import DefRPC


def count_to(n):
    print(f"counting to {n}...")
    for i in range(1, n + 1):
        print(i)


def main():

    print("\ndeferred sync request for add(1,2)")
    pi_rpc = DefRPC("add", args=[1, 2])
    pi_rpc.invoke(parallel_function=count_to, args=[10])


if __name__ == "__main__":
    main()
