# # `print_publication.py`
#
# Script for generating print items (weekly PDF, weekly epub).

# # Install requirements
#
# - Python
# - pandoc
# - python packages:
#   - ipython
#   - nbconvert
#   - nbformat
#   - pymupdf

import click
import os
import sys

from pathlib import Path

# import nbconvert
from natsort import natsorted
import nbformat
from nbconvert import HTMLExporter

# import pypandoc
import os
import secrets
import shutil
import subprocess
import fitz  # pip install pymupdf
from PIL import Image
import tempfile


def add_logo(pdf_output_dir, year=2023, logo_x=60, logo_y=40, size="L", scale=1.0, remove=False):
    # Add an OU logo to the first page of the PDF documents
    # Add copyright notice

    pkgdir = sys.modules["ou_print_pack_tools"].__path__[0]
    fullpath = Path(pkgdir) / "resources"
    if size != "L":
        if size == "S":
            logo_file = fullpath / "OU-logo-36x28.png"
            img = open(logo_file, "rb").read()
            logo_w, logo_h = img.size
        elif size == "M":
            logo_file = fullpath / "OU-logo-53x42.png"
            img = open(logo_file, "rb").read()
            logo_w, logo_h = img.size
        elif size == "C":
            logo_file = fullpath / "OU_Master_LOGO_BLACK_63mm.png"
            img = open(logo_file, "rb").read()
            logo_w, logo_h = Image.open(logo_file).size
    else:
        logo_file = fullpath / "OU_Master_LOGO_BLACK_63mm.png"
        image = Image.open(logo_file)
        logo_w, logo_h = image.size

        img = open(logo_file, "rb").read()

    logo_w = int(scale * logo_w)
    logo_h = int(scale * logo_h)

    # define the position (upper-left corner)
    logo_container = fitz.Rect(logo_x, logo_y, logo_x + logo_w, logo_y + logo_h)

    for f in natsorted(Path(pdf_output_dir).glob("*.pdf"), key=str):
        if f.name.endswith("_logo.pdf"):
            continue
        print(f"- branding: {f}")
        with fitz.open(f) as pdf:
            pdf_first_page = pdf[0]
            pdf_first_page.insert_image(logo_container, stream=img)
            pdf_out = f.name.replace(".pdf", "_logo.pdf")

            txt_origin = fitz.Point(350, 770)
            text = f"Copyright © The Open University, {year}"

            for page in pdf:
                page.insert_text(txt_origin, text)

            pdf.save(Path(pdf_output_dir) / pdf_out)
        # Remove the unbranded PDF
        if remove:
            os.remove(f)


@click.command()
@click.option(
    "--outdir",
    "-o",
    default="print_pack",
    help="Path to output dir [print_pack]",
    type=click.Path(),
)
@click.option("-y", "--year", type=click.STRING, default="2024", help="Copyright year")
@click.option("-X", "--logo-x", type=click.INT, default=60, help="Logo x co-ord")
@click.option("-Y", "--logo-y", type=click.INT, default=40, help="Logo y co-ord")
@click.option("-s", "--logo-scale", type=click.FLOAT, default=1.0, help="Logo scale")
@click.option(
    "-S", "--logo-size", type=click.STRING, default="L", help="Logo size: S, M, L"
)
def brandify(outdir, year, logo_x, logo_y, logo_scale, logo_size):
    """Brand a PDF with OU logo and copyright notice."""
    add_logo(outdir, year, logo_x, logo_y, logo_size, logo_scale)


@click.command()
@click.option(
    "-m",
    "--module",
    type=click.STRING,
    default="OU module",
    help="Module code and title",
)
@click.option(
    "--nbdir",
    "-n",
    default="content",
    help="Path to weekly content folders [content]",
    type=click.Path(exists=True),
)
@click.option(
    "--outdir",
    "-o",
    default="print_pack",
    help="Path to output dir [print_pack]",
    type=click.Path(),
)
@click.option("-y", "--year", type=click.STRING, default="2023", help="Copyright year")
def nb_to_print_pack(module, nbdir, outdir, year):
    """Generate print materials from Jupyter notebooks."""
    html_exporter = HTMLExporter(template_name="classic")

    pwd = Path.cwd()
    print(f"Starting in: {pwd}")

    # +
    nb_wd = nbdir  # "content" # Path to weekly content folders
    pdf_output_dir = outdir  # "print_pack" # Path to output dir

    # Create print pack output dir if required
    Path(pdf_output_dir).mkdir(parents=True, exist_ok=True)
    # -

    # Iterate through weekly content dirs
    # We assume the dir starts with a week number
    # or Part and the the week number
    print(Path(nb_wd))

    for p in natsorted(Path(nb_wd).glob("*[0-9]*"), key=str):
        if not p.is_dir():
            continue
        print(f"Rendering {p} to PDF")
        # Get the week number
        weeknum = p.name.split(". ")[0]

        # Settings for pandoc
        pdoc_args = [
            "-s",
            "-V geometry:margin=1in",
            "--toc",
            # f'--resource-path="{p.resolve()}"', # Doesn't work?
            "--metadata",
            f'title="{module} — Week {weeknum}"',
        ]

        # cd to week directory
        os.chdir(p)

        # Create a tmp directory for html files
        # Rather than use tempfile, create our own lest we want to persist it
        _tmp_dir = Path(secrets.token_hex(5))
        _tmp_dir.mkdir(parents=True, exist_ok=True)

        # Find notebooks for the current week
        for _nb in Path.cwd().glob("*.ipynb"):
            nb = nbformat.read(_nb, as_version=4)
            # Generate HTML version of document
            (body, resources) = html_exporter.from_notebook_node(nb)
            with open(_tmp_dir / _nb.name.replace(".ipynb", ".html"), "w") as f:
                f.write(body)

        module_code = module.split()[0]
        # print(_tmp_dir, os.listdir(_tmp_dir))

        # Now convert the HTML files to PDF
        # We need to run pandoc in the correct directory so that
        # relatively linked image files are correctly picked up.

        # Specify output PDF path
        pdf_out = str(pwd / pdf_output_dir / f"{module_code}_{weeknum}.pdf")
        epub_out = str(pwd / pdf_output_dir / f"{module_code}_{weeknum}.epub")

        # It seems pypandoc is not sorting the files in ToC etc?
        # pypandoc.convert_file(f"{temp_dir}/*html",
        #                   to='pdf',
        #                   #format='html',
        #                   extra_args=pdoc_args,
        #                   outputfile= str(pwd / pdf_output_dir / f"tm129_{weeknum}.pdf"))

        # Hacky - requires IPython
        # #! pandoc -s -o {pdf_out} -V geometry:margin=1in --toc --metadata title="TM129 Robotics — Week {weeknum}"  {_tmp_dir}/*html
        # #! pandoc -s -o {epub_out} --metadata title="TM129 Robotics — Week {weeknum}" --metadata author="The Open University, 2022" {_tmp_dir}/*html

        _command = f'pandoc --pdf-engine=xelatex --quiet -s -o "{pdf_out}" -V geometry:margin=1in --toc --metadata title="{module} — Week {weeknum}"  {_tmp_dir}/*html'

        subprocess.call(_command, shell=True)

        subprocess.call(
            f'pandoc --quiet -s -o "{epub_out}" --metadata title="TM129 Robotics — Week {weeknum}" --metadata author="The Open University, 2023" {_tmp_dir}/*html',
            shell=True,
        )

        # Tidy up tmp dir
        shutil.rmtree(_tmp_dir)

        # Just in case we need to know relatively where we are...
        # Path.cwd().relative_to(pwd)

        # Go back to the home dir
        os.chdir(pwd)

    os.chdir(pwd)

    add_logo(pdf_output_dir, year)
