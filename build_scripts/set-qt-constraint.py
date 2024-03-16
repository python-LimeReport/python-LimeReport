#!/usr/bin/env python3
import argparse

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('minver')
	args = ap.parse_args()

	p = 'pyproject.toml'

	with open(p, encoding='utf-8') as f:
		d = f.read()

	for pkg in ('PySide6', 'shiboken6', 'shiboken6_generator'):
		d = d.replace(f'"{pkg}"', f'"{pkg}=={args.minver}"')

	with open(p, 'w', encoding='utf-8') as f:
		f.write(d)

	with open('cibuildwheel/exclude_list.txt', encoding='utf-8') as f:
		d = f.read()
		
	major, minor, patch = args.minver.split('.')
	
	libraries = ['libshiboken6.abi3.so', 'libpyside6.abi3.so', 'libpyside6qml.abi3.so']

	for lib in libraries:
	    d = d.replace(f'{lib}.6.4', f'{lib}.{major}.{minor}')

	with open('cibuildwheel/exclude_list.txt', 'w', encoding='utf-8') as f:
		f.write(d)

if __name__ == '__main__':
	main()