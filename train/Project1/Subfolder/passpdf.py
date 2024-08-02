# test file
[x,y]
x = 10
y = 11
def myfunc():
    y = 123
    print("Python is " + x)
myfunc()

# Root nodes
module = "import math"

# Literals
num = 42
string = "Alice"
bytes_literal = b'hello'
ellipsis = ...
name_constant = True

# Variables
name = "x"

# Expressions
# bin_op 
2 + 3
2 - 3
2 // 3
2 * 3
2 % 3
2 ** 3
count = ~5
unary_op = -5
lambda_expr = lambda x: x * 2
# if_exp
if_exp = x if x > 0 else -x
if 1 == 2:
    print("something")
elif 2 == 2:
    print("something elif")
else:
    3
dict_literal = {'name': 'Alice', 'age': 30}
set_literal = {1, 2, 3}
list_comp = [x * x for x in range(5)]
set_comp = {x for x in range(10) if x % 2 == 0}
dict_comp = {word: len(word) for word in ['apple', 'banana']}
generator_exp = (x * x for x in range(5))
await_expr = await async_function()
yield_expr = yield 42
yield_from_expr = yield from another_generator()
compare_op = x < 5
call = print('Hello, world!')
subscript = my_list[2]
attribute = person.name
starred = *args
named_expr = (n := len(my_list)) > 0

# Compare
1 is 2
1 is not 2
1 in [1,2]
1 not in [1,2]
1 == 2
1 <= 2
1 >= 2
1 > 2
1 < 2
1 != 2

# Subscripting
index = my_list[0]
slice = my_list[1:3]
ext_slice = my_list[1:3, ...]

# Comprehensions
comprehension = [x for x in range(5)]

# Statements
# assign
x = 10
# aug_assign
count += 1
count -= 1
count *= 1
count /= 1
count //= 1
count %= 1
count @= 1
count **= 1
count &= 1
count |= 1
count ^= 1
count >>= 1
count <<= 1

# ann_assign
x: int = 42
# for_loop
for i in range(5):
    pass
# while_loop
while condition:
    pass
# if_stmt
if x > 0:
    pass
# else_stmt
else:
    print("hat")
# with_stmt
with open('file.txt', 'r') as f:
    pass
# raise_stmt
raise ValueError('Error message')
# try_except
try:
    pass
except Exception:
    pass
# assert_stmt
assert condition, 'Assertion failed'
# global_stmt
global x
# nonlocal_stmt
nonlocal y
# expr_stmt
print('Hello')
# pass_stmt
pass
# delete_stmt
del x
# return_stmt
return value
# break_stmt
break
# continue_stmt
continue

# Control Flow
# if_stmt
if condition:
    pass
# for_loop
for i in range(5):
    pass
# while_loop
while condition:
    pass
# try_except
try:
    pass
except Exception:
    pass
# with_stmt
with open('file.txt', 'r') as f:
    pass

# Pattern Matching
    match x:
        case 1:
            pass

# Type Parameters

# type_param
def generic_function(x: T) -> T:
    pass
# param_spec
def generic_function(x: P) -> P:
    pass
# constr
def generic_function(x: T) -> T:
    pass

# Function and Class Definitions
# function_def
def my_function(x):
    pass
# async_function_def
async def async_function():
    pass
# class_def
class MyClass:
    pass
# async_for
async for item in async_iterator:
    pass
# async_with
async with async_context_manager():
    pass

# Async and Await
# async_stmt
async def async_function():
    pass
# await_expr
await async_task()