

import numpy as np
import pandas as pd
import sqlite3 as sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
import joblib

from surprise import Reader, Dataset
from surprise.model_selection import cross_validate, GridSearchCV
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline
from surprise.model_selection import train_test_split

conn=sql.connect('data\\db_movies')
cur=conn.cursor() 

#######################################################################
#### 3 Sistema de recomendación basado en contenido KNN #################
#### Con base en todo lo visto por el usuario #######################
#######################################################################

movies=pd.read_sql('select * from movies2',conn)
movies.info()


##### cargar data frame escalado y con dummies ###

movies_dum1= joblib.load('salidas\\movies_dum1.joblib')

usuarios=pd.read_sql('select distinct (user_id) as user_id from ratings_final',conn)

def recomendar(user_id=list(usuarios['user_id'].value_counts().index)):
    
    ratings=pd.read_sql('select *from ratings_final where user_id=:user',conn, params={'user':user_id})
    l_movies_r=ratings['movie_id'].to_numpy()
    ####agregar la columna de movie_id y title de la pelicula a dummie para filtrar y mostrar nombre
    movies_dum1[['movie_id','title']]=movies[['movie_id','title']]

    ### filtrar peliculas calificadas por el usuario
    movies_r=movies_dum1[movies_dum1['movie_id'].isin(l_movies_r)]

    ## eliminar columna movie_id' y title
    movies_r=movies_r.drop(columns=['movie_id','title'])
    movies_r["indice"]=1 
    ##centroide o perfil del usuario
    centroide=movies_r.groupby("indice").mean() 

    ### filtrar peliculas no vistas    
    movies_nr=movies_dum1[~movies_dum1['movie_id'].isin(l_movies_r)] 
    
    ## eliminar movie_id y title
    movies_nr=movies_nr.drop(columns=['movie_id','title'])

    ### entrenar modelo 
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(movies_nr) 
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0]
    recomend_b=movies.loc[ids][['title','movie_id']]
    leidos=movies[movies['movie_id'].isin(l_movies_r)][['title','movie_id']]
    
    return recomend_b

recomendar(30)

print(interact(recomendar))