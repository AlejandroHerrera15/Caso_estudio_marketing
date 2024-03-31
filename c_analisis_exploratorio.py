import numpy as np 
import pandas as pd 
import sqlite3 as sql 
import plotly.graph_objs as go 
import a_funciones as fn 
from mlxtend.preprocessing import TransactionEncoder 
from datetime import datetime


conn=sql.connect('data\\db_movies')
cur=conn.cursor() ###para funciones que ejecutan sql en base de datos

movies=pd.read_sql('select* from movie2',conn)
ratings=pd.read_sql('select* from ratings2',conn)
ratings["view_time"]=pd.to_datetime(ratings['view_time'])

