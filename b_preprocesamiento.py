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

### EXPLORACIÓN INICIAL ###

### verificar duplicados y nulos

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
ratings['userId'].nunique()
ratings['movieId'].nunique()

#Las bases de movies y ratings no cuentan con datos duplicados ni nulos.

##### Exploración inicial de la base de ratings
calificaiones_cont=pd.read_sql(""" select 
                          "rating", 
                          count(*) as conteo 
                          from ratings 
                          group by "rating"
                          """, conn)


data  = go.Bar( x=calificaiones_cont.rating,y=calificaiones_cont.conteo, text=calificaiones_cont.conteo, textposition="outside")
Layout=go.Layout(title="Conteo de calificaciones",xaxis={'title':'Rating'},yaxis={'title':'Count'})
go.Figure(data,Layout)
# El gráfico de barras anterior ilustra la distribución de las calificaciones, 
# mostrando que las calificaciones de 4 y 3 tienen la mayor frecuencia, 
# mientras que las calificaciones de 0.5 y 1.5 son las menos comunes.


rating_users=pd.read_sql(''' select "UserId" as user_id,
                         count(*) as conteo
                         from ratings
                         group by "user_id"
                         order by conteo desc
                         ''',conn )

fig  = px.histogram(rating_users, x= 'conteo', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 

rating_users
# En el histograma anterior se evidencia la distribución de la cantidad de calificaciones 
# otorgadas por los usuarios. Destaca que el usuario que más califica tiene un número de calificaciones de 2698 películas, 
# mientras que la cantidad minima de calificaciones otorgadas por un usuario es de 20.
# La mayor cantidad de usuarios han calificado pocas peliculas, pero los que más tienen muchas.

#### excluir usuarios con menos de 40 peliculas calificados (para tener calificaion confiable) y los que tienen mas de mil porque pueden ser no razonables
rating_users2=pd.read_sql(''' select "UserId" as user_id,
                         count(*) as cnt_rat
                         from ratings
                         group by "UserId"
                         having cnt_rat >=40 and cnt_rat <=1000
                         order by cnt_rat desc
                         ''',conn )

fig  = px.histogram(rating_users2, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 


rating_movies=pd.read_sql(''' select movieId ,
                         count(*) as cnt_rat
                         from ratings
                         group by "movieId"
                         order by cnt_rat desc
                         ''',conn )

data  = go.Scatter(x = rating_movies.index, y= rating_movies.cnt_rat)
Layout= go.Layout(title="Ratings received per movie",xaxis={'title':'movie Count'}, yaxis={'title':'Ratings'})
go.Figure(data, Layout)
# Se puede interpretar del grafico anterior que hay una variación considerable en el número de calificaciones asignadas a cada película. 
# Por ejemplo, la película más popular ha recibido 329 calificaciones, mientras que hay películas que solo han sido calificadas una vez. 
# EPor consecuencia, resulta pertinente aplicar un filtro para incluir únicamente aquellas películas que han recibido un número significativo 
# de calificaciones para garantizar la validez del estudio.










