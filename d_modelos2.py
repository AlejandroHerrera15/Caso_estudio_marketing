

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
#### 3. Sistema de recomendación basado en contenido KNN #################
#### Con base en todo lo visto por el usuario #######################
#######################################################################

movies=pd.read_sql('select * from movies2',conn)
movies['año_estreno']=movies.año_estreno.astype('int')

movies.info()


##### cargar data frame escalado y con dummies ###

movies_dum1= joblib.load('salidas\\movies_dum1.joblib')

usuarios=pd.read_sql('select distinct (user_id) as user_id from ratings_final2',conn)

user_id=89

def recomendar(user_id=list(usuarios['user_id'].value_counts().index)):
    
    ratings=pd.read_sql('select *from ratings_final2 where user_id=:user',conn, params={'user':user_id})
    l_movies_r=ratings['movie_id'].to_numpy()
    ####agregar la columna de movie_id y title de la pelicula a dummie para filtrar y mostrar nombre
    movies_dum1[['movie_id','title']]=movies[['movieId','title']]

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
    recomend_b=movies.loc[ids][['title','movieId']]
    leidos=movies[movies['movieId'].isin(l_movies_r)][['title','movieId']]
    
    return recomend_b

recomendar(30)

print(interact(recomendar))

### ANALISIS:
### En este modelo, las películas son recomendadas a cada usuario basándose en todo su historial
### de observaciones en la plataforma. Esto proporciona un modelo robusto con suficiente 
### información para generar un conjunto de recomendaciones personalizado según los datos históricos de cada individuo.



############################################################################
##### 4. Sistema de recomendación filtro colaborativo #####
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

################# Entrenar con todos los datos y Realizar predicciones con el modelo afinado

trainset = data.build_full_trainset() ### esta función convierte todos los datos en entrnamiento, las funciones anteriores dividen  en entrenamiento y evaluación
model=gs_model.fit(trainset) ## se reentrena sobre todos los datos posibles (sin dividir)



predset = trainset.build_anti_testset() ### crea una tabla con todos los usuarios y las peliculas que no han calificado
#### en la columna de rating pone el promedio de todos los rating, en caso de que no pueda calcularlo para un item-usuario
len(predset)

predictions = gs_model.test(predset) ### función muy pesada, hace las predicciones de rating para todas las peliculas que no ha visto un usuario
### la funcion test recibe un test set constriuido con build_test method, o el que genera crosvalidate

predictions_df = pd.DataFrame(predictions) ### esta tabla se puede llevar a una base donde estarán todas las predicciones
predictions_df.shape
predictions_df.head()
predictions_df['r_ui'].unique() ### promedio de ratings.
predictions_df.sort_values(by='est',ascending=False)

def recomendaciones(user_id,n_recomend=10):
    
    predictions_userID = predictions_df[predictions_df['uid'] == user_id].\
                    sort_values(by="est", ascending = False).head(n_recomend)

    recomendados = predictions_userID[['iid','est']]
    recomendados.to_sql('reco',conn,if_exists="replace")
    
    recomendados=pd.read_sql('''select a.*, b.title 
                             from reco a left join movies_f b
                             on a.iid=b.movieId ''', conn)

    return(recomendados)


 
recomendaciones(user_id=500,n_recomend=10)

### ANALISIS:
### En la evaluación de los modelos para realizar predicciones, se consideran métricas como
### MAE (Error Absoluto Medio), RMSE (Error Cuadrático Medio), tiempo de ajuste (fit time) y tiempo de prueba (test time). 
### Se observa que todos los modelos muestran resultados muy similares en estas métricas por lo que se prefirió priorizar el desempeño en el tiempo de procesamiento
### por lo que se eligió  el knns.KNNWithMeans.
### En este modelo, se utilizan las calificaciones de los usuarios para sugerir películas al usuario seleccionado, priorizando las estimaciones más altas. 
### Este enfoque es más fiable cuando hay un mayor número de calificaciones por película.

