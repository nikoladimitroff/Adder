from time import sleep
from copy import deepcopy
import sys

from adder import proplogic
from adder import search
from adder import problem



EAGLE = r"""
                             /T /I
                              / |/ | .-~/
                          T\ Y  I  |/  /  _
         /T               | \I  |  I  Y.-~/
        I l   /I       T\ |  |  l  |  T  /
     T\ |  \ Y l  /T   | \I  l   \ `  l Y
 __  | \l   \l  \I l __l  l   \   `  _. |
 \ ~-l  `\   `\  \  \\ ~\  \   `. .-~   |
  \   ~-. "-.  `  \  ^._ ^. "-.  /  \   |
.--~-._  ~-  `  _  ~-_.-"-." ._ /._ ." ./
 >--.  ~-.   ._  ~>-"    "\\   7   7   ]
^.___~"--._    ~-{  .-~ .  `\ Y . /    |
 <__ ~"-.  ~       /_/   \   \I  Y   : |
   ^-.__           ~(_/   \   >._:   | l______
       ^--.,___.-~"  /_/   !  `-.~"--l_ /     ~"-.
              (_/ .  ~(   /'     "~"--,Y   -=b-. _)
               (_/ .  \  :           / l      c"~o \
                \ /    `.    .     .^   \_.-~"~--.  )
                 (_/ .   `  /     /       !       )/
                  / / _.   '.   .':      /        '
                  ~(_/ .   /    _  `  .-<_
                    /_/ . ' .-~" `.  / \  \          ,z=.
                    ~( /   '  :   | K   "-.~-.______//
                      "-,.    l   I/ \_    __{--->._(==.
                       //(     \  <    ~"~"     //
                      /' /\     \  \     ,v=.  ((
                    .^. / /\     "  }__ //===-  `
                   / / ' '  "-.,__ {---(==-       -Row
                 .^ '       :  T  ~"   ll       
                / .  .  . : | :!        \\
               (_/  /   | | j-"          ~^
                 ~-<_(_.^-~"""


TOUCAN = r"""
           _ _.-''''''--._
         .` `.  ...------.\
        / |O :-`   _,.,---'
       '  \   ;--''
       | _.' (
       ,' _,' `-.
       : /       '.
       \ \         '
        `.|         `.
          `-._        \
              '.  ,-.  \
  .__          _`.\..`\ \
  ,  ''- . _,-'.,-'  ``: \
  '-...._ (( (('-.._    \ \
         `--..      `'-. \ \
              `..     '   \ \
                 `\ \fsr   `" 
                   \/"""

WINNIE = r"""
                            _.
                ,-.,-"`""-./  \
               /   \        `-.|       .:::.:::.
               \   /           `-._    :::::::::
               |                 "=\    ':::::'
               |        .=="    |o_|_     ':'
               |         _o.     ` (_)          ,;;;,;;;,
               ;                     \\         ;;;;;;;;;
                \             _.     /|-.        ';;;;;'
                 \           ` `'---'/   \         ';'
                  \       .--._     /-'   |
                 ,-`.    /     `-._(     /
                 `-._`-._\         `\   '\
                   ( `    `'._  _,   |    \
                   /    ~-.   `|     |    |
                  /        `;-.|     |    |
                .'  \         /|     |    /
              .'-.   '.      | \     |  .'
              `-._     '.    |       /"` `\
               /  `"--.,_'-._\-.___.'_     ;
              /          `''';--'     `.   |
             /            .'`            \ /''-.
            ;            /                \''-, \
            |           /                 |    \ |
            \           |          '.           |/
             '.          \         .'`-.        /
               '._        '.,___,.;'    '-.___.'
                  `'''----------'`"""

def copy_image_part(src, dest, src_coords, dest_coords, length):
    for row in range(length[0]):
        for col in range(length[1]):
            i1, j1 = row + src_coords[0], col + src_coords[1]
            i2, j2 = row + dest_coords[0], col + dest_coords[1]
            dest[i2][j2] = src[i1][j1]


def draw_image(state, image, buffer, size):
    step_row = len(buffer) // size
    step_col = len(buffer[0]) // size

    for index, pos in enumerate(state):
        pos = int(pos)
        dest_coords = step_row * (index // size), step_col * (index % size)
        src_coords = step_row * (pos // size), step_col * (pos % size)
        copy_image_part(buffer, image, src_coords, dest_coords, (step_row, step_col))

    
    image_lines = "\n".join(["".join(line) for line in image])
    print("*" * 100)
    print(image_lines)
    print("*" * 100)


def main():
    images = {"eagle": EAGLE, "toucan": TOUCAN, "winnie": WINNIE}
    args = sys.argv[2:]
    art = images[args[0] if len(sys.argv) > 1 else "eagle"]
    lines = art.split("\n")[1:]
    rows = len(lines)
    columns = max(len(line) for line in lines)
    buffer = []
    for line in lines:  
        buffer_line = line + " ".join(["" for i in range(columns - len(line) + 1)])
        buffer.append(list(buffer_line))
        
    
    initial, goal = ("4 2 5 3 6 8 1 7 0", "0 1 2 3 4 5 6 7 8")
    factory = problem.ProblemFactory()
    problem_instance = factory.from_npuzzle(initial, goal)
    heuristic = factory.heuristic_for(problem_instance)

    
    size = int(len(goal.replace(" ", "")) ** 0.5)
    step_row = len(buffer) // size
    step_col = len(buffer[0]) // size

    for i in range(step_row):
        for j in range(step_col):
            buffer[i][j] = "#"


    solution = search.astar(problem_instance, heuristic)
    image = deepcopy(buffer)
    for state, action in solution:
        draw_image(state, image, buffer, size)
        sleep(0.25)

main()