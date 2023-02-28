# ou-print-pack-tools

Tools to support production of OU print packs from Jupyter notebooks, quarto files, etc.

Support currently exists for:

- generating OU branded PDF documents (one per notebook directory);
- generating epub books (one per notebook directory).

The intention is that the package can also be used as part of a GitHub Action automation script to generate print pack assets directly from content committed to a GitHub repository.

```text
Usage: ou_nb_print_pack [OPTIONS]

  Generate print materials from Jupyter notebooks.

Options:
  -n, --nbdir PATH   Path to weekly content folders [content]
  -o, --outdir PATH  Path to output dir [print_pack]
  --help             Show this message and exit.
```
