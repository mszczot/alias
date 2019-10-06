from alias.classes import ExtensionType, ArgumentationFramework


a = ArgumentationFramework('test')
a.add_argument('a')
a.add_argument('b')
a.add_argument('c')
a.add_argument('d')
a.add_argument('e')
a.add_argument('f')
a.add_attack(('a', 'b'))
a.add_attack(('b', 'f'))
a.add_attack(('f', 'c'))
a.add_attack(('c', 'd'))
a.add_attack(('c', 'e'))
a.add_attack(('d', 'e'))
a.add_attack(('e', 'd'))

print(a.get_complete_extension())
print(a.get_stable_extension())
