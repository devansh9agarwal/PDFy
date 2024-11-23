import re
from collections import defaultdict, deque

COL = 5
_S = 30

init = []
fin = []
init_dfa = []
fin_dfa = []


def initialise(table_NFA):
    for i in range(1000):
        for j in range(COL):
            table_NFA[i][j] = -1

def print_initial_final():
    print("Initial state/s is/are :- ", end="")
    print(" ".join(str(x) for x in init))
    print("Final state/s is/are :- ", end="")
    print(" ".join(str(x) for x in fin))

def print_initial_final_dfa():
    print("Initial state/s is/are :- ", end="")
    print(" ".join(init_dfa))
    print("Final state/s is/are :- ", end="")
    print(" ".join(fin_dfa))
    print("\n" + "-"*60)

def reduce_fin(x):
    global fin
    fin = fin[:x] + fin[x + 1:]

def preprocessor(s):
    x = ['(']
    for i in range(len(s)):
        x.append(s[i])
        if s[i].isalpha() and i + 1 < len(s) and s[i+1].isalpha():
            x.append('.')
        elif s[i] == ')' and i + 1 < len(s) and s[i + 1] == '(':
            x.append('.')
        elif s[i].isalpha() and i + 1 < len(s) and s[i + 1] == '(':
            x.append('.')
        elif s[i] == ')' and i + 1 < len(s) and s[i + 1].isalpha():
            x.append('.')
        elif s[i] == '*' and i + 1 < len(s) and (s[i + 1] == '(' or s[i + 1].isalpha()):
            x.append('.')
    x.append(')')
    return ''.join(x)

def postfix(s):
    a = []
    ch = deque()
    for x in s:
        if x == 'a' or x == 'b':
            a.append(x)
        elif x == '(':
            ch.append('(')
        elif x == ')':
            while ch:
                if ch[-1] == '(':
                    ch.pop()
                    break
                else:
                    a.append(ch.pop())
        elif x == '.':
            while ch and ch[-1] in ['.', '*']:
                a.append(ch.pop())
            ch.append('.')
        elif x == '|':
            while ch and ch[-1] in ['.', '*']:
                a.append(ch.pop())
            ch.append('|')
        elif x == '*':
            ch.append('*')

    while ch:
        a.append(ch.pop())

    return ''.join(a)

def re_to_nfa(s, table_NFA):
    global init, fin
    states = 1
    for x in s:
        if x == 'a':
            table_NFA[states][0] = states
            init.append(states)
            states += 1
            table_NFA[states - 1][1] = states
            fin.append(states)
            states += 1
        elif x == 'b':
            table_NFA[states][0] = states
            init.append(states)
            states += 1
            table_NFA[states - 1][2] = states
            fin.append(states)
            states += 1
        elif x == '.':
            m = fin[-2]
            n = init[-1]
            table_NFA[m][3] = n
            reduce_fin(-2)
        elif x == '|':
            for count in range(2):
                m = init[-(count + 1)]
                table_NFA[states][3 + count] = m
            init = init[:-2] + [states]
            states += 1
            for count in range(2):
                m = fin[-(count + 1)]
                table_NFA[m][3] = states
            fin = fin[:-2] + [states]
            states += 1
        elif x == '*':
            m = init[-1]
            table_NFA[states][3] = m
            init[-1] = states
            states += 1
            n = fin[-1]
            table_NFA[n][3] = m
            table_NFA[n][4] = states
            table_NFA[states - 1][4] = states
            fin[-1] = states
            states += 1
    return states

def print_NFA_table(table_NFA, states):
    print("\n" + "*" * 60)
    print("TRANSITION TABLE FOR NFA")
    print(f"{'States':>10} {'a':>10} {'b':>10} {'e1':>10} {'e2':>10}")
    print("-" * 60)
    for i in range(1, states):
        print(f"{i:>10}", end="")
        for j in range(COL):
            print(f"{table_NFA[i][j]:>10}" if table_NFA[i][j] != -1 else f"{'--':>10}", end="")
        print()
    print("*" * 60)
    print_initial_final()

def print_DFA_table(table_DFA, state):
    print("\n" + "*" * 60)
    print("TRANSITION TABLE FOR DFA")
    print(f"{'States':>10} {'a':>10} {'b':>10}")
    print("-" * 60)
    for i in range(state):
        print(f"{table_DFA[i][0]:>10} {table_DFA[i][1]:>10} {table_DFA[i][2]:>10}")
    print("*" * 60)
    print_initial_final_dfa()

def e_closure(table_NFA, x):
    s = [x]
    m = {x: 1}
    while s:
        y = s.pop()
        if table_NFA[y][3] != -1:
            s.append(table_NFA[y][3])
            m[table_NFA[y][3]] = 1
            if table_NFA[y][4] != -1:
                s.append(table_NFA[y][4])
                m[table_NFA[y][4]] = 1
    return list(m.keys())

def NFA_to_DFA(table_NFA, states, table_DFA):
    flag = [True] * states
    state = 0
    j = 0
    m_STATE = {}
    v = e_closure(table_NFA, init[0])
    flag[init[0]] = False
    m_STATE[tuple(v)] = f"q{j}"
    j += 1
    init_dfa.append(m_STATE[tuple(v)])
    if fin[0] in v:
        fin_dfa.append(m_STATE[tuple(v)])

    st = [v]
    count = 0
    while st:
        v = st.pop()
        table_DFA[state][0] = m_STATE[tuple(v)]
        v1 = []
        v3 = []

        for i in v:
            flag[i] = False
            if table_NFA[i][1] != -1:
                v1.append(table_NFA[i][1])
            if table_NFA[i][2] != -1:
                v3.append(table_NFA[i][2])

        v2 = []
        v4 = []
        for i in v1:
            v2 += e_closure(table_NFA, i)
        for i in v3:
            v4 += e_closure(table_NFA, i)

        if v2:
            table_DFA[state][1] = m_STATE.get(tuple(v2), f"q{j}")
            if tuple(v2) not in m_STATE:
                m_STATE[tuple(v2)] = f"q{j}"
                j += 1
                st.append(v2)
        else:
            table_DFA[state][1] = "--"

        if v4:
            table_DFA[state][2] = m_STATE.get(tuple(v4), f"q{j}")
            if tuple(v4) not in m_STATE:
                m_STATE[tuple(v4)] = f"q{j}"
                j += 1
                st.append(v4)
        else:
            table_DFA[state][2] = "--"

        state += 1

    print_DFA_table(table_DFA, state)
    return state

def valid_CHECK(word):
    return all(c in 'ab' for c in word)

def simulator(table_DFA, word, state):
    if not valid_CHECK(word):
        print("String does not belong to the given RE.")
        return

    temp = init_dfa[0]
    for i in word:
        for j in range(state):
            if table_DFA[j][0] == temp:
                temp = table_DFA[j][1 if i == 'a' else 2]
                break
        if temp == "--":
            print("String does not belong to the given RE.")
            return

    if temp in fin_dfa:
        print("String belongs to the given RE.")
    else:
        print("String does not belong to the given RE.")

if __name__ == "__main__":
    table_NFA = [[-1 for _ in range(COL)] for _ in range(1000)]
    table_DFA = [["" for _ in range(3)] for _ in range(1000)]

    s = input("Enter the regular expression (in terms of a and b): ")
    s = preprocessor(s)
    print(f"Regular Expression after preprocessing: {s}")
    s = postfix(s)
    print(f"Regular Expression in postfix: {s}")

    initialise(table_NFA)
    states = re_to_nfa(s, table_NFA)
    print_NFA_table(table_NFA, states)

    state = NFA_to_DFA(table_NFA, states, table_DFA)

    while True:
        word = input("Enter the string to check (Enter 'exit' to stop): ")
        if word == "exit":
            break
        simulator(table_DFA, word, state)
