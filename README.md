Bibliophile's Dream
-------------------

[National Novel Generation Month](https://github.com/NaNoGenMo/2016) has kicked
off, and this year I'm going to take a stab. Based on Google's [Deep Dream](https://github.com/google/deepdream), I'm going to train a neural net on books (probably from [Gutenberg](https://www.gutenberg.org/), but we'll see), then run it backwards and see what gets generated.

Step 0: Project Setup
=====================

Download and install TensorFlow

Install the gutenberg pip module:
```
pip install gutenberg
```

Step 1: Obtaining Texts
=======================

Download from Gutenberg, with category data for each.

Probably need to trim off the legal boilerplate.

Step 2: Train the Net
=====================

I'll base this on [TensorFlow](https://www.tensorflow.org/).

Step 3: Run It Backwards
========================

Base this on the code samples at [Deep Dream](https://github.com/google/deepdream).
