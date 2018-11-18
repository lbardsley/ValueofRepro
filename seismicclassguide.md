{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Guide to run Tensorflow classifier"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Steps to follow"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### 1. Convert the image files to jpg and save in a convenient directory\n",
    "\n",
    "My file for this is seismicneural.ipynb saved in the repo\n",
    "I ended up copying the jpg files over to a directory close to home `C:\\Users\\niall\\rguhack\\notebooks`"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Only save the train images in here - but you can use most of the set for training\n",
    "\n",
    "Save the images in separate folders according to the classifications you want.  I saved them  in two directories `final_train_jpg` and `raw_train_jpg` "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### 2. Install tensorflow -hub"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "I assume you already have tensorflow installed using pip or conda. In addition you need to install a pre-trained classifier model called tensorflow -hub.\n",
    "You can do this with pip install - the instructions at this link\n",
    "https://www.tensorflow.org/hub/installation"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### 3. Run the classification\n",
    "\n",
    "In the terminal type the following all in a single line\n",
    "\n",
    "`python hub/examples/image_retraining/retrain.py --how_many_training_steps 100 --image_dir=C:/Users/niall/rguhack/notebooks/training_data`\n",
    "\n",
    "It took ages to figure out this command properly - make sure and save -hub in the directory you're opening the terminal in annd for the `image-dir` command make sure you type the full directory\n",
    "\n",
    "You can play around with the training steps parameter.  I ran one with just 50 and it still gave excellent results\n",
    "\n",
    "For 100 steps this took me around 15 minutes of training"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "#### 4. Use your classifier\n",
    "\n",
    "This also took a while to figure out.  I'm sure Mike will be able to do something really efficient in C++ to make this more user friendly.\n",
    "\n",
    "The instructions for use are here but aren't easy to follow:\n",
    "\n",
    "https://www.tensorflow.org/hub/tutorials/image_retraining#using_the_retrained_model\n",
    "\n",
    "I had to find the label_image.py file somehwere else but it's in the repo now for convenience.  Copy it into your main directiry so it can run more easily.\n",
    "\n",
    "I just tested 'test'  images individually with weirdly accurate results.  Here's the command I ran:\n",
    "\n",
    "`python label_image.py --graph=/tmp/output_graph.pb --labels=/tmp/output_labels.txt --input_layer=Placeholder --output_layer=final_result --image=c\\Users\\niall\\rguhack\\ESP2D_RAW_FULL_KPSTM_STACK_059B064_4900_5000.jpg`\n",
    "\n",
    "This is a raw image example and I returned the following result:\n",
    "\n",
    "raw train jpg 0.9285909\n",
    "final_train jpg 0.0714\n",
    "\n",
    "So this is saying with 93% certainty this image i passed it was 'raw'.  I ran a few and got simiar results.  Quite spooky (or over fitted!?)\n",
    "\n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
