if __name__ == '__main__':

    if (len(argv[1:]) <= 1):
        print(color_red)
        print("请输入正确的参数")
        help()
        exit(0)
    cmd = argv[1]
    ip = argv[2]
    try:
