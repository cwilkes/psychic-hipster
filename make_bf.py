from pybloomfilter import BloomFilter
import sys
import os


def make_writers(number_attributes, number_elements, output_dir, error_rate):
    ret = list()
    for _ in range(number_attributes):
        output_file = os.path.join(output_dir, 'attr_%d.bloom' % (_,))
        ret.append(BloomFilter(number_elements, error_rate, output_file))
    print >>sys.stderr, 'Number hashes: %d, Number bits: %d' % (ret[0].num_hashes, ret[0].num_bits)
    return ret


def main(args):
    args = args[1:]
    attribute_writers = make_writers(int(args.pop(0)), int(args.pop(0)), args.pop(0), 0.1)
    for line_no, line in enumerate(_.strip() for _ in sys.stdin):
        for pos, letter in enumerate(line):
            if letter == '1':
                attribute_writers[pos].add(line_no)
        if line_no % 1000 == 0:
            print >>sys.stderr, map(len, attribute_writers)
    for bf in attribute_writers:
        bf.close()
    print >>sys.stderr, map(len, attribute_writers)


if __name__ == '__main__':
    main(sys.argv)
