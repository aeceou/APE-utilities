import argparse
import itertools
import os
import re
import shutil
from numpy.random import permutation

def txt_len(files):
    counts = []
    for f in files:
        count = 0
        for line in f:
            count += 1
        counts.append(count)
    for i in range(len(counts)):
        if i >= 1:
            assert counts[i] == counts[i-1]
    return counts[0]


def has_empty_lines(lines):
    empty = False
    for line in lines:
        if re.sub(r"(\W)+", "", line) == '':
            empty = True
            break
    return empty


def is_too_long(lines, max_len):
    too_long = False
    for line in lines:
        if len(line.split()) > max_len:
            too_long = True
            break
    return too_long


class TextShuffler(object):
    def __init__(self, args):
        self.opts = args

        # Input files
        self.in_files = []
        for suffix in args.suffices:
            in_file_path = self.opts.in_prefix + '.' + suffix
            in_file = open(in_file_path, 'r', encoding=self.opts.enc)
            self.in_files.append(in_file)
        
        # Just to calculate the length of the given files
        tmp_files = []
        for i, in_file in enumerate(self.in_files):
            tmp_file, orig_file = itertools.tee(in_file)
            tmp_files.append(tmp_file)
            self.in_files[i] = orig_file
        self.in_file_len = txt_len(tmp_files)

        # To fit the data into the memory
        self.max_mem = self.opts.max_mem
        self.mem_splits = []
        remaining = self.in_file_len
        if remaining < self.max_mem:
            self.max_mem = remaining
        while remaining > self.max_mem:
            self.mem_splits.append(self.max_mem)
            remaining -= self.max_mem
        if remaining > 0:
            self.mem_splits.append(remaining)

        # Output files
        self.out_file_paths = []
        for i, suffix in enumerate(args.suffices):
            out_file_path = self.opts.out_prefix + '.' + suffix
            self.out_file_paths.append(out_file_path)

    def macro_shuffle(self):
        self.cut = self.opts.cut
        remaining = self.in_file_len
        if remaining < self.cut:
            # Change the input files
            self.in_files = []
            for suffix in args.suffices:
                in_file_path = self.opts.in_prefix + '.' + suffix
                in_file = open(in_file_path, 'rb')
                self.in_files.append(in_file)
            return
        
        self.cuts = []
        while remaining > self.cut:
            self.cuts.append(self.cut)
            remaining -= self.cut
        if remaining > 0:
            self.cuts.append(remaining)

        in_file_dir = os.path.dirname(self.opts.in_prefix)
        if in_file_dir == '':
            in_file_dir = os.getcwd()
        buffer_dir = os.path.join(in_file_dir, 'shuffle_buffer')
        os.makedirs(buffer_dir, exist_ok=True)

        shuffle_map = permutation(len(self.cuts)).tolist()
        buffer_idx = 0
        shuffle_idx = shuffle_map[buffer_idx]
        buffer_len = self.cuts[buffer_idx]
        data = []

        count = 0
        for lines in zip(*self.in_files):
            if count < buffer_len:
                data.append(lines)
                count += 1
            else:
                for i, suffix in enumerate(self.opts.suffices):
                    buffer_path = os.path.join(
                        buffer_dir,
                        f'{shuffle_idx+1}.{suffix}')
                    with open(buffer_path, 'w', encoding=self.opts.enc)\
                        as buffer_file:
                        for datum in data:
                            buffer_file.write(datum[i])

                count, data = 1, [lines]
                buffer_idx += 1
                if buffer_idx < len(self.cuts):
                    shuffle_idx = shuffle_map[buffer_idx]
                    buffer_len = self.cuts[buffer_idx]

        # The last pieces
        for i, suffix in enumerate(self.opts.suffices):
            buffer_path = os.path.join(
                buffer_dir,
                f'{shuffle_idx+1}.{suffix}')
            with open(buffer_path, 'w', encoding=self.opts.enc)\
                as buffer_file:
                for datum in data:
                    buffer_file.write(datum[i])

        # Merge all buffer slices
        for i in range(1, (len(self.cuts) + 1)):
            for suffix in self.opts.suffices:
                if i == 1:
                    os.system(f'cat {buffer_dir}/{i}.{suffix} > {in_file_dir}/macro_shuffled.{suffix}')
                else:
                    os.system(f'cat {buffer_dir}/{i}.{suffix} >> {in_file_dir}/macro_shuffled.{suffix}')
        
        # Change the input files
        self.in_files = []
        for suffix in args.suffices:
            in_file_path = os.path.join(in_file_dir,
                                        'macro_shuffled' + '.' + suffix)
            in_file = open(in_file_path, 'rb')
            self.in_files.append(in_file)

        # Remove the buffer directory
        shutil.rmtree(buffer_dir)

    def micro_shuffle(self):
        shuffle_maps = [permutation(self.mem_splits[i]).tolist() for i
                        in range(len(self.mem_splits))]
        mem_idx = 0
        shuffle_map = shuffle_maps[mem_idx]
        max_mem = len(shuffle_map)
        data = []

        count = 0
        for lines in zip(*self.in_files):
            if count < max_mem:
                data.append(lines)
                count += 1
            else:
                shuffled = []
                for j, lines in enumerate(data):
                    shuffled.append(data[shuffle_map[j]])
                self.write(shuffled)

                count, data = 1, [lines]
                mem_idx += 1
                if mem_idx < len(self.mem_splits):
                    shuffle_map = shuffle_maps[mem_idx]
                    max_mem = len(shuffle_map)

        # The last pieces
        shuffled = []
        for j, lines in enumerate(data):
            shuffled.append(data[shuffle_map[j]])
        self.write(shuffled)

    def write(self, data: list[tuple[str]]):
        out_files = []
        for out_file_path in self.out_file_paths:
            out_file = open(out_file_path, 'a')
            out_files.append(out_file)

        for lines in data:
            # Python's UTF-8 decoder treat non-UTF-8 characters
            # as special codepoints U+DC00 – U+DCFF (which are normally illegal in UTF-8).
            # Afterwards, they should be re-decoded as something else.
            lines = [re.sub(r"[\udc00-\udcff]+",
                            lambda m: (m.group(0).encode("utf-8")\
                                                 .decode(self.opts.enc)),
                            line.decode('utf-8')) for line in lines]
            # Basic filtering
            if not (has_empty_lines(lines) or is_too_long(lines, self.opts.max_len)):
                for i, out_file in enumerate(out_files):
                    out_file.write(lines[i])

        for out_file in out_files:
            out_file.close()


def main(args):
    machine = TextShuffler(args)
    machine.macro_shuffle()
    machine.micro_shuffle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-in_prefix", "--input_prefix",
                        type=str, dest='in_prefix')
    parser.add_argument("-out_prefix", "--output_prefix",
                        type=str, dest='out_prefix')
    parser.add_argument('-suffix', '--suffices', nargs='*', required=False,
                        default=['src', 'mt', 'pe'])
    parser.add_argument("-enc", "--encoding",
                        type=str, required=False, default='utf-8',
                        dest='enc')
    parser.add_argument("-cut", "--cut", type=int, required=False,
                        default='100000')
    parser.add_argument("-max_mem", "--maximum_memory",
                        type=int, required=False, default='100000',
                        dest='max_mem')
    parser.add_argument("-max_len", "--maximum_length",
                        type=int, dest='max_len')

    args = parser.parse_args()
    main(args)
