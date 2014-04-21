import sys
import random
from bitarray import bitarray
from multiprocessing import Manager


def read_rule_lines(lines):
    my_rules = list()
    for line in (_.strip() for _ in lines):
        if line and not line.startswith('#'):
            try:
                my_rules.append(eval(line))
            except Exception as ex:
                raise Exception('Bad line "%s"' % (line, ), ex)
    return my_rules


def row_maker(number_attributes, percent_min, percent_max, rules):
    my_rand_percent = lambda _: percent_min + (percent_max-percent_min)*random.random()
    # ie [0.1, 0.2, 0.01] for percent chance that an element is a 1 vs 0
    bit_chance = map(my_rand_percent, range(number_attributes))
    # calling this produces a new row based on those percentages
    raw_row = lambda: bitarray((random.random()*100 < percent for percent in bit_chance))
    # applies all the rules from the rule file to a new row

    def my_func():
        elements = raw_row()
        for rule in rules:
            for bit_offset, val in rule(elements):
                elements[bit_offset] = val
        return elements
    return my_func


def produce_n_rows(config, queue, lock):
    print >>sys.stderr, 'C1'
    my_rand_percent = lambda _: config[1] + (config[2]-config[1])*random.random()
    # ie [0.1, 0.2, 0.01] for percent chance that an element is a 1 vs 0
    bit_chance = map(my_rand_percent, range(config[0]))
    # calling this produces a new row based on those percentages
    raw_row = lambda: bitarray((random.random()*100 < percent for percent in bit_chance))
    print >>sys.stderr, 'C2'
    rules = read_rule_lines(config[4])
    print >>sys.stderr, 'C2'
    try:
        print >>sys.stderr, 'C3', type(lock)
    except Exception as ex:
        print >>sys.stderr, 'ex', ex
    while lock.acquire(False):
        print >>sys.stderr, 'C3'
        queue.put(rules(raw_row()).to01())
        print >>sys.stderr, 'C4'
    print >>sys.stderr, 'C5'
    queue.put(-1)
    print >>sys.stderr, 'done'


def write_out_rows(queue, writer, number_queue_writer):
    while number_queue_writer > 0:
        e = queue.get()
        if e == -1:
            number_queue_writer -= 1
        else:
            writer.write(e)
            writer.write('\n')


def setup(args, reader):
    _number_elements = 200000
    if args:
        _number_elements = int(args.pop(0))
    if args:
        random.seed(int(args.pop(0)))
    lines = (_.strip() for _ in reader)
    number_attributes = int(next(lines))
    percent_min, percent_max = (float(_) for _ in next(lines).split())
    raw_rules = list(lines)
    return _number_elements, (number_attributes, percent_min, percent_max, raw_rules)


if __name__ == '__main__':
    number_elements, _config = setup(sys.argv[1:], sys.stdin)

    manager = Manager()
    number_threads = 4
    pool = manager.Pool(number_threads)
    q = manager.Queue()
    s = manager.Semaphore(number_elements)

    print >>sys.stderr, 'Starting up %d threads with config %s' % (number_threads, _config)
    for _ in range(number_threads):
        #pool.apply_async(produce_n_rows, args=(_config, q, s))
        pool.apply_async(produce_n_rows, args=(_config, None, None))
        #produce_n_rows(config, q, s)

    _writer = sys.stdout
    write_out_rows(q, _writer, number_threads)
