

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

usuarios=pd.read_sql('select distinct (user_id) as user_id from ratings_final2',conn)

user_id=312

def recomendar(user_id=list(usuarios['user_id'].value_counts().index)):
    
    ratings=pd.read_sql('select *from ratings_final2 where user_id=:user',conn, params={'user':user_id})
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


############################################################################
#####4 Sistema de recomendación filtro colaborativo #####
############################################################################

### datos originales en pandas
ratings=pd.read_sql('select * from ratings_final where movie_rating>0', conn)

####los datos deben ser leidos en un formato espacial para surprise
reader = Reader(rating_scale=(0, 10)) ### la escala de la calificación
###las columnas deben estar en orden estándar: user item rating
data   = Dataset.load_from_df(ratings[['user_id','movie_id','movie_rating']], reader)

# 
models=[KNNBasic(),KNNWithMeans(),KNNWithZScore(),KNNBaseline()] 
results = {}

###knnBasiscs: calcula el rating ponderando por distancia con usuario/Items
###KnnWith means: en la ponderación se resta la media del rating, y al final se suma la media general
####KnnwithZscores: estandariza el rating restando media y dividiendo por desviación 
####Knnbaseline: calculan el desvío de cada calificación con respecto al promedio y con base en esos calculan la ponderación

#### for para probar varios modelos ##########
model=models[1]
for model in models:
 
    CV_scores = cross_validate(model, data, measures=["MAE","RMSE"], cv=5, n_jobs=-1)  
    
    result = pd.DataFrame.from_dict(CV_scores).mean(axis=0).\
             rename({'test_mae':'MAE', 'test_rmse': 'RMSE'})
    results[str(model).split("algorithms.")[1].split("object ")[0]] = result


performance_df = pd.DataFrame.from_dict(results).T
performance_df.sort_values(by='RMSE')

###################se escoge el mejor knn withmeans#########################
param_grid = { 'sim_options' : {'name': ['msd','cosine'], \
                                'min_support': [7,2], \
                                'user_based': [False, True]}
             }

## min support es la cantidad de items o usuarios que necesita para calcular recomendación
## name medidas de distancia

### se afina si es basado en usuario o basado en ítem

gridsearchKNNWithMeans = GridSearchCV(KNNBaseline, param_grid, measures=['rmse'], \
                                      cv=2, n_jobs=-1)
                                    
gridsearchKNNWithMeans.fit(data)


gridsearchKNNWithMeans.best_params["rmse"]
gridsearchKNNWithMeans.best_score["rmse"]
gs_model=gridsearchKNNWithMeans.best_estimator['rmse'] ### mejor estimador de gridsearch

