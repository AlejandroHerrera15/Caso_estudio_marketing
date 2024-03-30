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
##traer tabla de BD a python ##

movies= pd.read_sql("""select *  from movies""", conn)
ratings = pd.read_sql('select * from ratings', conn)


#########################################
############# Exploración ###############
#########################################

### Identificar campos de cruce y verificar que estén en mismo formato ####
### verificar duplicados

movies.info()
movies.head()
movies.duplicated().sum()
movies.isnull().sum()
movies.shape

ratings.info()
ratings.head()
ratings.duplicated().sum()
ratings.isnull().sum()
ratings.shape
#Las bases no tienen datos duplicados ni nulos.


###### Exploración de Ratings #######

cr=pd.read_sql(""" select 
                          "rating", 
                          count(*) as conteo 
                          from ratings 
                          group by "rating"
                          """, conn)


data  = go.Bar( x=cr.rating,y=cr.conteo, text=cr.conteo, textposition="outside")
Layout=go.Layout(title="Count of ratings",xaxis={'title':'Rating'},yaxis={'title':'Count'})
go.Figure(data,Layout)

#El conteo de clasificaciónes nos muestra como las puntuaciones de '4' y '3' son las que tienen
#una mayor participación, las calificaciónes con menor participación son las de '0.5', '1' y '1.5'.


rating_users=pd.read_sql(''' select "UserId" as user_id,
                         count(*) as cnt_rat
                         from ratings
                         group by "UserId"
                         order by cnt_rat desc
                         ''',conn )


data  = go.Scatter(x = rating_users.index, y= rating_users.cnt_rat)
Layout= go.Layout(title="Ratings given per user",xaxis={'title':'User Count'}, yaxis={'title':'Ratings'})
go.Figure(data, Layout) 










