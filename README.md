# ou-print-pack-tools

Tools to support production of OU print packs from Jupyter notebooks, quarto files, etc.

__Requires `pandoc`__ ;  on a Mac, also run:

```
brew install basictex

sudo tlmgr update --self
sudo tlmgr install multirow svg trimspaces transparent
```

Support currently exists for:

- generating OU branded PDF documents (one per notebook directory);
- generating epub books (one per notebook directory).

The intention is that the package can also be used as part of a GitHub Action automation script to generate print pack assets directly from content committed to a GitHub repository.

```text
Usage: ou_nb_print_pack [OPTIONS]

  Generate print materials from Jupyter notebooks.

Options:
  -m, --module TEXT  Module code and title
  -n, --nbdir PATH   Path to weekly content folders [content]
  -o, --outdir PATH  Path to output dir [print_pack]
  -y, --year TEXT    Copyright year
  --help             Show this message and exit.
```

```text
Usage: ou_pdf_brandify [OPTIONS]

  Brand a PDF with OU logo and copyright notice.

Options:
  -o, --outdir PATH       Path to output dir [print_pack]
  -y, --year TEXT         Copyright year
  -X, --logo-x INTEGER    Logo x co-ord
  -Y, --logo-y INTEGER    Logo y co-ord
  -s, --logo-scale FLOAT  Logo scale
  -S, --logo-size TEXT    Logo size: S, M, L
  --help                  Show this message and exit.
```
