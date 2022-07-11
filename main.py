# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from app import doAllTheStuff


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    with open('detect_sample.txt') as sample_file:
        sample_textt = sample_file.read()
    if doAllTheStuff(sample_textt) == 'POSITIVE':
        print("Approved")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
