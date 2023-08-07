from setuptools import setup

setup(
    name="ou_print_pack_tools",
    packages=["ou_print_pack_tools"],
    version='0.0.3',
    author="Tony Hirst",
    author_email="tony.hirst@gmail.com",
    description="Generate print packs from Jupyter notebooks.",
    long_description='''
    Generate OU branded print packs from Jupyter notebooks.
    ''',
    long_description_content_type="text/markdown",
    install_requires=["click",
                      "ipython",
                      "nbconvert",
                      "nbformat",
                      "pymupdf",
                      "natsort"
                      ],
    include_package_data=True,
    package_data={'': ['resources/*']},
    entry_points='''
        [console_scripts]
        ou_nb_print_pack=ou_print_pack_tools.print_publication:nb_to_print_pack
        ou_nb_brandify=ou_print_pack_tools.print_publication:brandify
    '''
)