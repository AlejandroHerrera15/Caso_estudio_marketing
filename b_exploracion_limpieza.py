import numpy as np
import pandas as pd
import sqlite3 as sql
import plotly.graph_objs as go ### para gráficos
from mlxtend.preprocessing import TransactionEncoder #para separar los géneros
import plotly.express as px
from datetime import datetime 
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
# Esta observación sugiere que no es necesario aplicar un filtro en relación a estas variables, ya que con un mínimo de 20 calificaciones se pueden obtener resultados fiables.


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
# Por consecuencia, resulta pertinente aplicar un filtro para incluir únicamente aquellas películas que han recibido un número significativo 
# de calificaciones para garantizar la validez del estudio.

## LIMPIEZA Y TRANSFORMACIONES ##

## En SQL se filtran las películas que no tienen más de 10 calificaciones.
fn.ejecutar_sql('preprocesamiento.sql', cur)

pd.read_sql('select count(*) ratings_f', conn)
ratings =pd.read_sql('select * from  ratings_f',conn)

pd.read_sql('select count(*) movies_f', conn)
movies =pd.read_sql('select * from  movies_f',conn)

pd.read_sql('select count(*) ratings_final', conn)
df_final = pd.read_sql('select * from  ratings_final',conn)

###### Para separar géneros en base de datos
genres=movies['genres'].str.split('|')
te = TransactionEncoder()
genres = te.fit_transform(genres)
genres = pd.DataFrame(genres, columns = te.columns_)
genres  = genres.astype(int)
movies = movies.drop(['genres'], axis = 1) 
movies =pd.concat([movies, genres],axis=1)
#Eliminamos la variable movieId:1 que no es necesaria
movies = movies.drop(['movieId:1'], axis = 1) 

###### Extraer año de la variable titulo
movies['año_estreno'] = movies['title'].str[-5:-1]

###### Conviertiendo la variable timestamp a datetime
if 'timestamp' in ratings.columns:
    # Convertir 'timestamp' a formato de fecha
    ratings['fecha_vista'] = pd.to_datetime(ratings['timestamp'], unit='s')

    # Eliminar la columna 'timestamp'
    ratings.drop(['timestamp'], axis=1, inplace=True)
    
    # Eliminar hora de fecha
    ratings['fecha_vista'] = ratings['fecha_vista'].dt.date


###### Limpieza para base combinada final
genres2=df_final['genres'].str.split('|')
te2= TransactionEncoder()
genres2 = te2.fit_transform(genres2)
genres2 = pd.DataFrame(genres2, columns = te2.columns_)
genres2  = genres2.astype(int)
df_final = df_final.drop(['genres'], axis = 1) 
df_final =pd.concat([df_final, genres2],axis=1)
#Eliminamos la variable movieId:1 que no es necesaria
df_final = df_final.drop(['movieId:1'], axis = 1) 

###### Extraer año de la variable titulo
df_final['año_estreno'] = df_final['title'].str[-5:-1]

###### Conviertiendo la variable timestamp a datetime
if 'timestamp' in df_final.columns:
    # Convertir 'timestamp' a formato de fecha
    df_final['fecha_vista'] = pd.to_datetime(df_final['timestamp'], unit='s')

    # Eliminar la columna 'timestamp'
    df_final.drop(['timestamp'], axis=1, inplace=True)
    
    # Eliminar hora de fecha
    df_final['fecha_vista'] = df_final['fecha_vista'].dt.date


movies.to_sql('movies2',conn, index=False, if_exists='replace')
base_movies=pd.read_sql('select * from movies2',conn)

ratings.to_sql('ratings2', conn, index=False, if_exists='replace')
base_ratings=pd.read_sql('''select * from ratings2''',conn)

df_final.to_sql('ratings_final2', conn, index=False, if_exists='replace')
base_completa = pd.read_sql('''select * from ratings_final2''',conn)

base_ratings
base_movies
base_completa


conn.close()
#Cerrar conexion de base de datos






