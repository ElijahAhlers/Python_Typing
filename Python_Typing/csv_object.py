import csv
import os


class csv_object:

    def __init__(self, filename=None, header=None):

        self.filename = filename
        self.header = header
        self.body = []

        if filename and os.path.isfile(filename):
            with open(filename, 'r') as file_read:
                file_contents = [line for line in csv.reader(file_read)]
                self.header = file_contents[0]
                for line_contents in file_contents[2:]:
                    self.body += [{self.header[i]:item for i, item in enumerate(line_contents)}]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.header and self.body:
            with open(self.filename, 'w') as file_write:
                file_write.write(','.join(self.header)+'\n\n')
                for line in self.body:
                    file_write.write(','.join([str(line[header]) for header in self.header])+'\n')


if __name__ == "__main__":
    with csv_object(filename='test_file.csv') as file:
        print('Header:', file.header)
        print("_________")
        print("Body:", file.body)
