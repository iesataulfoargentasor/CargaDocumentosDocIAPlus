#!/bin/zsh
cd "${0:A:h}"
.venv/bin/python run.py
read '?Pulsa Intro para cerrar...'
