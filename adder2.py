### Same as adder.py but uses a different method of indexing into lists, not sure if there's a performance benefit

from z3 import *

BITLEN = 1 # Number of bits in input
STEPS = 1 # How many steps to take (e.g. time)
WIDTH = 2 # How many operations/values can be stored in parallel, has to be at least BITLEN * #inputs

# Input variables
x = BitVec('x', BITLEN)
y = BitVec('y', BITLEN)


s = Solver()
steps = []

# Define operations used
op_list = [BitVecRef.__and__, BitVecRef.__or__, BitVecRef.__xor__, BitVecRef.__xor__]
unary_op_list = [BitVecRef.__invert__]
for uop in unary_op_list:
    op_list.append(lambda x, y : uop(x))

# Chooses a function to use by setting all others to 0
def chooseFunc(i, x, y):
    res = 0
    for ind, op in enumerate(op_list):
        res = res + (ind == i) * op(x, y)
    return res

# Chooses an input to use by setting all others to 0
def chooseVar(step_ind, ind):
    res = 0
    for i, node in enumerate(steps[step_ind]):
        res = res + (i == ind) * node
    return res

# First step is just the bits of the input padded with constants
firststep = []
for i in range(BITLEN):
    firststep.append(Extract(i, i, x))
    firststep.append(Extract(i, i, y))
for i in range(BITLEN * 2, WIDTH):
    firststep.append(BitVec("const_0_%d" % i, 1))
steps.append(firststep)

# Generate remaining steps
for i in range(1, STEPS + 1):
    this_step = []
    last_step = steps[-1]

    for j in range(WIDTH):
        func_ind = Int("func_%d_%d" % (i,j))
        s.add(func_ind >= 0, func_ind < len(op_list))

        x_ind = Int("x_%d_%d" % (i,j))
        s.add(x_ind >= 0, x_ind < WIDTH)

        y_ind = Int("y_%d_%d" % (i,j))
        s.add(y_ind >= 0, y_ind < WIDTH)

        x_var = chooseVar(i - 1, x_ind)
        y_var = chooseVar(i - 1, y_ind)

        node = chooseFunc(func_ind, x_var, y_var)
        this_step.append(node)

    steps.append(this_step)

# Set the result to the first BITLEN bits of the last step
if BITLEN == 1:
    result = steps[-1][0]
else:
    result = Concat(*steps[-1][:BITLEN])

# Set goal
goal = x | y
s.add(ForAll([x, y], goal == result))

print(s)
print(s.check())
print(s.model())
