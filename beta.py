# http://127.0.0.1:5000/
import numpy as np
from load_tables import load_tables
#from html_tooltips import make_html_fig
from arxiv import get_article
from collections import OrderedDict
from flask import Flask, request
from flask import render_template
# from astropy.table import Table
from flask import session
from bokeh_plot import do_a_plot
import pandas as pd
import pickle

app = Flask(__name__)

app.secret_key = "23B9FD8E7EAE4964FD4F15F857DB7"

# Render the front page
@app.route('/')
def index():
    return render_template('index.html')


# Parse form entry to load_tex and return result
@app.route('/find-tables', methods=["POST"])
def scrape():
    arxiv_number = str(request.form["arxiv_number"])
    get_article("{0}".format(arxiv_number))
    data_list, header_list, unit_list = load_tables(arxiv_number)
    return render_template('data.html', ntables=len(data_list),
                           header="{0}".format(header_list[0]),
                           data="{0}".format(data_list[0]),
                           arxiv_number=arxiv_number)


# Display table and select variables
@app.route('/table/<arxiv_number>/<int:tnumber>', methods=["GET", "POST"])
def select_variables(arxiv_number, tnumber):
    table, headers, data, ncolumns, nrows = format_data(arxiv_number, tnumber)
    return render_template('table.html', header_list=headers, data=data,
                           ncolumns=ncolumns, nrows=nrows,
                           arxiv_number=arxiv_number, tnumber=tnumber)


# test inserting figure
@app.route('/table/<arxiv_number>/<int:tnumber>/figure')
def make_figure(arxiv_number, tnumber):
    table, headers, data, ncolumns, nrows = format_data(arxiv_number, tnumber)
    do_a_plot(table)
    # t = session.get("tab")  # load the json of the data
    # panda = pd.read_json(t)  # parse this to bokeh
    # arr = panda.as_matrix().T
    # table = make_html_fig(arr)
    # do_a_plot(panda)
    return render_template('bokeh_plot.html')


def format_data(arxiv_number, tnumber):
    data_list, header_list, unit_list = load_tables(arxiv_number)
    headers, data = header_list[tnumber], data_list[tnumber]  # select table
    headers = [i.replace("$", "") for i in headers]  # clean up data
    headers = [i.replace("\\", "") for i in headers]  # clean up data
    ncolumns, nrows = len(headers), len(data)
    mydict = OrderedDict(zip(headers, data.T))  # make a dictionary of data
    table = pd.DataFrame(mydict)  # make a pandas dataframe of data
    # session["tab"] = table.to_json()  # convert pandas df to json
    return table, headers, data, ncolumns, nrows


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
