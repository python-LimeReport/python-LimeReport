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

	d = d.replace('libshiboken6.abi3.so.6.4', f'"libshiboken6.abi.so.{major}.{minor}"')
	d = d.replace('libpyside6.abi3.so.6.4', f'"libpyside6.abi.so.{major}.{minor}"')
	
	with open('cibuildwheel/exclude_list.txt', 'w', encoding='utf-8') as f:
		f.write(d)

if __name__ == '__main__':
	main()