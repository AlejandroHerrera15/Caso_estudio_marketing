import numpy as np 
import pandas as pd 
import a_funciones as fn 
import sqlite3 as sql 
from datetime import datetime
import plotly.graph_objs as go 
from mlxtend.preprocessing import TransactionEncoder


conn=sql.connect('data\\db_movies')
cur=conn.cursor()

movies=pd.read_sql('select * from movies2',conn)
ratings=pd.read_sql('select * from ratings2',conn)

movies
ratings

