#!/bin/zsh
cd "${0:A:h}"
.venv/bin/python scripts/configurar_aws.py
read '?Pulsa Intro para cerrar...'