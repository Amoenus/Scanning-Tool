import ast, os, re
from collections import defaultdict

repo = r"C:\Git\Scanning-Tool"
py_files = []
for root, dirs, files in os.walk(repo):
    if root.startswith(os.path.join(repo, '.git')):
        continue
    if any(skip in root for skip in ['.venv', 'venv', 'env', 'site-packages']):
        continue
    for name in files:
        if name.endswith('.py'):
            py_files.append(os.path.join(root, name))
py_files.sort()


def normalize_lines(lines):
    out = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        s = re.sub(r"\s+", " ", s)
        out.append(s)
    return out


def file_source(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().splitlines()


def get_blocks(path):
    src = file_source(path)
    try:
        tree = ast.parse('\n'.join(src), filename=path)
    except SyntaxError:
        return []
    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', None)
            if end is None:
                continue
            block = src[start:end]
            norm = normalize_lines(block)
            if len(norm) >= 4:
                blocks.append((norm, path, start + 1, end, type(node).__name__, node.name))
    return blocks

func_map = defaultdict(list)
for path in py_files:
    for norm, path, start, end, typ, name in get_blocks(path):
        key = '\n'.join(norm)
        func_map[key].append((path, start, end, typ, name))

dups = []
for key, items in func_map.items():
    if len(items) > 1:
        dups.append((len(items), len(key.splitlines()), items))
dups.sort(key=lambda x: (-x[0], -x[1]))

print('FUNCTION/METHOD/CLASS BODY DUPLICATES:')
for count, length, items in dups[:30]:
    print(f'\nDuplicate body of {length} normalized lines appears {count} times:')
    for path, start, end, typ, name in items:
        print(f'  - {typ} {name} in {os.path.relpath(path, repo)}:{start}-{end}')

min_block = 12
block_occurrences = defaultdict(list)
for path in py_files:
    lines = normalize_lines(file_source(path))
    for i in range(len(lines) - min_block + 1):
        block = '\n'.join(lines[i:i + min_block])
        block_occurrences[block].append((path, i + 1, i + min_block))

exact_dups = [(len(v), v) for v in block_occurrences.values() if len(v) > 1]
exact_dups.sort(reverse=True, key=lambda x: (x[0],))
print('\nEXACT {}-LINE BLOCK DUPLICATES:'.format(min_block))
for count, items in exact_dups[:20]:
    print(f'\nBlock repeated {count} times:')
    for path, start, end in items[:10]:
        print(f'  - {os.path.relpath(path, repo)}:{start}-{end}')

print('\nSCANNED FILES:', len(py_files))
