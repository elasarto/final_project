import numpy as np 
import pandas as pd 
import math

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect
)

from markov_generator import RhymeGenerator

app=Flask(__name__)
gen = RhymeGenerator("markov.pickle", "markov_rev.pickle")

@app.route('/')
def home():
    """Return the dashboard homepage."""
    return render_template('markov.html')

@app.route('/<input>')
def generator(input):
    return gen.generate(input)

if __name__ == "__main__":
    app.run(debug=True)
