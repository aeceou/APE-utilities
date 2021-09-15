class TER_Result:
    def __init__(self, file):

        self.text = open(file, "rt").readlines()

        scores = list()
        lengths = list()

        i = 0
        while i < len(self.text) - 1:
            if i >= 5:
                if i >= len(self.text) - 2:
                    break
                else:
                    scores.append(float(self.text[i].split("|")[8].strip()))
                    lengths.append(float(self.text[i].split("|")[7].strip()))
            else:
                pass
            i += 1

        self.scores = scores
        self.lengths = lengths
