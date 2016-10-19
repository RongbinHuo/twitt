def some_func(line):
  str_ary = line.split(',')
  del str_ary[6]
  return ','.join(str_ary)

filename = '/Users/rongbin/duck_tape/fixtures/media/stations.csv'
altered_lines = []
with open(filename, "r") as f:
    lines = (line.rstrip() for line in f)
    for line in lines:
      altered_line = some_func(line)
      altered_lines.append(altered_line)
with open(filename, "w") as f:
    f.write('\n'.join(altered_lines) + '\n')


