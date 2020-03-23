if __name__ == '__main__':

    if (len(argv[1:]) <= 1):
        print(color_red)
        print("Please input right params")
        help()
        exit(0)
    cmd = argv[1]
    ip = argv[2]
    try:
