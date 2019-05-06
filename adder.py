from z3 import *

BITLEN = 4 # Number of bits in input
STEPS = 0 # How many steps to take in between input and output layers (e.g. time)
WIDTH = 8 # How many operations/values can be stored in parallel, has to be at least BITLEN * #inputs

# Input variables
x = BitVec('x', BITLEN)
y = BitVec('y', BITLEN)

# Define operations used
op_list = [BitVecRef.__and__, BitVecRef.__or__, BitVecRef.__xor__]
unary_op_list = [BitVecRef.__invert__]
for uop in unary_op_list:
    op_list.append(lambda x, y : uop(x))

# Chooses a function to use by setting all others to 0
def chooseFunc(i, x, y):
    res = 0
    for ind, op in enumerate(op_list):
        res = If(ind == i, op (x, y), res)
    return res

s = Solver()
steps = []

# First step is just the bits of the input padded with constants
firststep = Array("firststep", IntSort(), BitVecSort(1))
for i in range(BITLEN):
    firststep = Store(firststep, i * 2, Extract(i, i, x))
    firststep = Store(firststep, i * 2 + 1, Extract(i, i, y))
for i in range(BITLEN * 2, WIDTH):
    firststep = Store(firststep, i, BitVec("const_0_%d" % i, 1))
steps.append(firststep)

# Generate remaining steps
for i in range(1, STEPS + 2):
    final_step = i == STEPS + 1

    this_step = Array("finalstep" if final_step else "step_%d" % i, IntSort(), BitVecSort(1))
    last_step = steps[-1]

    for j in range(BITLEN if final_step else WIDTH):
        func_ind = Int("func_%d_%d" % (i,j))
        s.add(func_ind >= 0, func_ind < len(op_list))

        x_ind = Int("x_%d_%d" % (i,j))
        s.add(x_ind >= 0, x_ind < WIDTH)

        y_ind = Int("y_%d_%d" % (i,j))
        s.add(y_ind >= 0, y_ind < WIDTH)

        node = chooseFunc(func_ind, Select(last_step, x_ind), Select(last_step, y_ind))
        this_step = Store(this_step, j, node)

    steps.append(this_step)

# Set the result to the concatenated bits of the last step
if BITLEN == 1:
    result = Select(steps[-1], 0)
else:
    result = Concat(*[Select(steps[-1], i) for i in range(BITLEN)])

# Set goal
goal = x | y
s.add(ForAll([x, y], goal == result))

print(s)
print(s.check())
print(s.model())
