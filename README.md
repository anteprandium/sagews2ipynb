

# sagew2ipynb

This little script converts a Sage Math Cloud online worksheet, (`.sagews`) into an iPython notebook (`.ipynb`), with engine Sage 6.6. This is  useful because iPython notebooks are the only format common to both Sage in local mode and Sage Math Cloud, so you can push/pull files as needed.

See folder examples for an example of a converted notebook.

## Images

The image inclusion is completely untested.

## SVG

So far, SVG inclusion works partially. If you open the notebook with ipython, you get

    <IPython.core.display.SVG Object>

instead of an image, but if you subsequently export the notebook to html, with

     sage -ipython nbconvert SAGETEST.ipynb --to html

then the exported html does indeed show the svg drawing in its full pixel-less glory.

See [this html](./examples/SAGETEST.html) versus [this notebook](./examples/SAGETEST.ipynb)

It also works properly if you export to latex (though this is provided converting the SVG to PDF): 

     sage -ipython nbconvert SAGETEST.ipynb --to latex
     




--- @anteprandium

