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

if __name__ == '__main__':
	main()