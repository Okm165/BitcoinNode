import utils.utilities as UT
import datetime

class Logs:
    def __init__(self, logging_file_path) -> None:
        self.logging_file_path = logging_file_path
        self.log_file = open(self.logging_file_path, "a")
        self.log = []

    def update(self, string):
        self.log.append(string)

    def flush(self):
        if not len(self.log): return
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " "
        string = time
        for log in self.log:
            string += log + "\n"
            if len(self.log) > 1:
                string += UT.dent(len(time))

        self.log_file.write(string)
        self.log = []

    def close(self):
        self.log_file.close()