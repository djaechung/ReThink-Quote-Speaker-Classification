test_string = "Hello world!"
test_dict = {"Hello": "world!"}
test_list = test_string.split()
def test_func(_str):
    my_str = _str.split()
    for i in range(len(my_str)):
        print(f"word {i}: {my_str[i]}")
    return my_str


