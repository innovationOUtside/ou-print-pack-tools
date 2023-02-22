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



from pathlib import Path
#import nbconvert
import nbformat
from nbconvert import HTMLExporter
#import pypandoc
import os
import secrets
import shutil
import subprocess
import fitz #pip install pymupdf

html_exporter = HTMLExporter(template_name = 'classic')

pwd = Path.cwd()
print(f'Starting in: {pwd}')

# +
nb_wd = "content" # Path to weekly content folders
pdf_output_dir = "print_pack" # Path to output dir

# Create print pack output dir if required
Path(pdf_output_dir).mkdir(parents=True, exist_ok=True)
# -

# Iterate through weekly content dirs
# We assume the dir starts with a week number
for p in Path(nb_wd).glob("[0-9]*"):
    print(f'- processing: {p}')
    if not p.is_dir():
        continue

    # Get the week number
    weeknum = p.name.split(". ")[0]
    
    # Settings for pandoc
    pdoc_args = ['-s', '-V geometry:margin=1in',
             '--toc',
             #f'--resource-path="{p.resolve()}"', # Doesn't work?
             '--metadata', f'title="TM129 Robotics — Week {weeknum}"']
    
    #cd to week directory
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
            
    # Now convert the HTML files to PDF
    # We need to run pandoc in the correct directory so that
    # relatively linked image files are correctly picked up.
    
    # Specify output PDF path
    pdf_out = str(pwd / pdf_output_dir / f"tm129_{weeknum}.pdf")
    epub_out = str(pwd / pdf_output_dir / f"tm129_{weeknum}.epub")
    
    # It seems pypandoc is not sorting the files in ToC etc?
    #pypandoc.convert_file(f"{temp_dir}/*html",
    #                   to='pdf',
    #                   #format='html',
    #                   extra_args=pdoc_args,
    #                   outputfile= str(pwd / pdf_output_dir / f"tm129_{weeknum}.pdf"))
    
    # Hacky - requires IPython
    # #! pandoc -s -o {pdf_out} -V geometry:margin=1in --toc --metadata title="TM129 Robotics — Week {weeknum}"  {_tmp_dir}/*html
    # #! pandoc -s -o {epub_out} --metadata title="TM129 Robotics — Week {weeknum}" --metadata author="The Open University, 2022" {_tmp_dir}/*html
    subprocess.call(f'pandoc --quiet -s -o {pdf_out} -V geometry:margin=1in --toc --metadata title="TM129 Robotics — Week {weeknum}"  {_tmp_dir}/*html', shell = True)
    subprocess.call(f'pandoc --quiet -s -o {epub_out} --metadata title="TM129 Robotics — Week {weeknum}" --metadata author="The Open University, 2022" {_tmp_dir}/*html', shell = True)

    # Tidy up tmp dir
    shutil.rmtree(_tmp_dir)
    
    #Just in case we need to know relatively where we are...
    #Path.cwd().relative_to(pwd)
    
    # Go back to the home dir
    os.chdir(pwd)

os.chdir(pwd)

# ## Add OU Logo to First Page of PDF
#
# Add an OU logo to the first page of the PDF documents

# +
logo_file = ".print_assets/OU-logo-83x65.png"
img = open(logo_file, "rb").read()

# define the position (upper-left corner)
logo_container = fitz.Rect(60,40,143,105)

for f in Path(pdf_output_dir).glob("*.pdf"):
    print(f'- branding: {f}')
    with fitz.open(f) as pdf:
        pdf_first_page = pdf[0]
        pdf_first_page.insert_image(logo_container, stream=img)
        pdf_out = f.name.replace(".pdf", "_logo.pdf")
        
        txt_origin = fitz.Point(350, 770)
        text = "Copyright © The Open University, 2022"
        
        for page in pdf:
            page.insert_text(txt_origin, text)

        pdf.save(Path(pdf_output_dir) / pdf_out)
    #Remove the unbranded PDF
    os.remove(f)
# -


