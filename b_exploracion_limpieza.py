import numpy as np
import pandas as pd
import sqlite3 as sql
import plotly.graph_objs as go ### para gráficos
import plotly.express as px
import a_funciones as fn


###### para ejecutar sql y conectarse a bd ###

conn=sql.connect('data\\db_movies') ### crear cuando no existe el nombre de cd  y para conectarse cuando sí existe.
cur=conn.cursor() ###para funciones que ejecutan sql en base de datos

### para verificar las tablas que hay disponibles
cur.execute("SELECT name FROM sqlite_master where type='table' ")
cur.fetchall()


#######
############ traer tabla de BD a python ####

movies= pd.read_sql("""select *  from movies""", conn)
ratings = pd.read_sql('select * from ratings', conn)

#####Exploración inicial #####

### Identificar campos de cruce y verificar que estén en mismo formato ####
### verificar duplicados

movies.info()
movies.head()
movies.duplicated().sum() 

ratings.info()
ratings.head()
ratings.duplicated().sum()

