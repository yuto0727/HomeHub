import coding_test_import as c
import global_val as g

a = 1
# g.b = 100

def test():
    global a
    a = 10

def main():
    print(a, g.b)
    test()
    c.add_number()
    print(a, g.b)

if __name__ == "__main__":
    main()