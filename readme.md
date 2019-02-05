# op-bean-compare

A simple command line utility to compare the transactions of OP (Osuuspankki) bank account statements and
Beancount ledger. Reports possible missing transactions in Beancount ledger which are in the OP's ledger.
Personal utility for my plaintext accounting system.

## Installation
Run the following command in the directory root:
```
pip3 install .
```

## Usage
```
usage: op-bean-compare [-h] [--strict [STRICT]] beancount op start end

Compare OP and Beancount ledgers and report differences

positional arguments:
  beancount          Path the to OP-ledger file
  op                 Path the to OP-ledger csv
  start              Starting date as ISO-date
  end                Ending date as ISO-date

optional arguments:
  -h, --help         show this help message and exit
  --strict [STRICT]  Enable strict mode
```
