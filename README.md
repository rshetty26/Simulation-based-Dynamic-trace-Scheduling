In a programming language of your choice among {C, Java, Python, C++} [note, your makefile must ensure that the correct version of python is invoked on CSE machines, i.e. be explicit in whether to invoke the python3 or python2.7 interpreter], implement a program with the following specification that performs dynamic (OoO) scheduling with conservative load-store ordering on a restricted set of simplified instructions:

Your program will take one command line input, a filename, and output its results in a file named **out.txt**

Format of input file:

The input file will consist of a first line with two comma separated (no whitespace) positive integers followed by between 1-256 lines of a format described below. The two integers on the first line will specify the number of physical registers in the system and the issue width of the machine. **All machine resources will match issue width, and the number of physical registers will always be greater than 32.** If not, the program should produce an empty output file.

Each subsequent line will contain one of the following "instructions" R,REG,REG,REG

I,REG,REG,IMM

L,REG,IMM,REG

S,REG,IMM,REG

where {R,I,L,S} are the capital letters R, I, L, and S, {,} is comma, REG is a positive integer value between 0 and 31, inclusive, and IMM is a POSITIVE integer value between 0 and 65535, with both REG and IMM encoded as decimals. The first REG is the destination for R, I, and L. Memory (not modeled) is the destination for S.

Assuming:

- Pipeline stages = FE,DE,RE,DI,IS,WB,CO
- No fetch/decode stalls (equivalent to unbounded queue between DE and RE)
- The first instruction is always fetched in cycle 0
- The initial architectural to physical mappings are A0-P0, A1-P1...A31-P31 and all other physical registers are on the free list in increasing register order (i.e. the next register consumed in renaming will always be P32)
- All memory operations hit in the cache, and all instructions writeback in the cycle following their issue.

produce the following output in out.txt:

For each instruction in the input file, produce a corresponding line in out.txt of the form

FE,DE,RE,DI,IS,WB,CO

where all comma-separated fields are non-negative integers encoded as decimals and represent the cycle in which the associated instruction completes the specified stage. For simplicity, assume that S-class instructions occupy WB in the cycle after they issue.

Note that the following restrictions with regard to register freeing and conservative load-store scheduling apply: registers freed at commit in a cycle (N) are not available on the free list until the following cycle (N+1), and that potentially dependent memory operations cannot issue in the same cycle.

Reminder: You are not allowed to copy large pieces (or the entirety) of OoO simulator code from the web wholesale (yes, people have done this. No, submitting a random MIPS simulator doesn't actually fulfill the assignment specifications and is a base score of 0 in addition to an AI violation...) That said, you are welcome to look over the SimpleScalar documentation for inspiration, noting for instance, the structure of its primary simulation loop.

Example input-output pairs will be provided in the modules directory for your testing benefit.
