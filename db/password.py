import bcrypt

if __name__ == '__main__':
    print('Enter a password')
    password = input()
    print(password)
    password = password.encode('utf-8')
    # Hash a password for the first time, with a randomly-generated salt
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(hashed.decode('utf-8'))
    # Check that an unhashed password matches one that has previously been
    # hashed
    if bcrypt.checkpw(password, hashed):
        print("It Matches!")
    else:
        print("It Does not Match :(")
