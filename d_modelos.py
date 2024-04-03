import numpy as np
import pandas as pd
import sqlite3 as sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
import joblib
#### conectar_base_de_Datos


conn=sql.connect('data\\db_movies')
cur=conn.cursor() 

#movies = pd.read_sql('select * from movies2', conn)
#ratings = pd.read_sql('select * from ratings2', conn)
#final = pd.read_sql('select * from ratings_final2', conn)


#####################################################################
################## 1. sistemas basados en popularidad ###############
#####################################################################


##### recomendaciones basado en popularidad ######

#### mejores calificadas
pd.read_sql("""select title, 
            avg(movie_rating) as avg_rat,
            count(*) as conteo_calificaiones
            from ratings_final2
            where movie_rating<>0
            group by title
            order by avg_rat desc
            limit 10
            """, conn)

#### Peliculas más vistas con promedio de los que calficaron ###
pd.read_sql("""select title, 
            avg(iif(movie_rating = 0, Null, movie_rating)) as avg_rat,
            count(*) as conteo_calificaiones
            from ratings_final2
            group by title
            order by conteo_calificaiones desc
            limit 10
            """, conn)

#### los mejores calificados por año publicacion ###
pd.read_sql("""select año_estreno, title, 
            avg(iif(movie_rating = 0, Null, movie_rating)) as avg_rat,
            count(iif(movie_rating = 0, Null, movie_rating)) as conteo_rat
            from ratings_final2
            group by  año_estreno, title
            order by año_estreno desc, avg_rat desc limit 20
            """, conn)




##############################################################################################
######## 2. Sistema de recomendación basado en contenido KNN un solo producto visto #########
##############################################################################################

movies=pd.read_sql('select * from movies2',conn)
movies.info()
movies['año_estreno']=movies.año_estreno.astype('int')
movies.info()

##### escalar para que año esté en el mismo rango ###
sc=MinMaxScaler()
movies[["año_estreno_sc"]]=sc.fit_transform(movies[['año_estreno']])

##### eliminar filas que no se van a utilizar ###
movies_dum1=movies.drop(columns=['movieId','title','conteo','año_estreno'])

joblib.dump(movies_dum1,"salidas\\movies_dum1.joblib") ### para utilizar en segundos modelos

##### ### entrenar modelo #####

model = neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
model.fit(movies_dum1)
dist, idlist = model.kneighbors(movies_dum1)


distancias=pd.DataFrame(dist) ## devuelve un ranking de la distancias más cercanas para cada fila(pelicula)
id_list=pd.DataFrame(idlist) ## para saber esas distancias a que item corresponde


####ejemplo para una pelicula
movie_list_name = []
movie_name='Toy Story (1995)'
movie_id = movies[movies['title'] == movie_name].index ### extraer el indice
movie_id = movie_id[0] ## si encuentra varios solo guarde uno

for newid in idlist[movie_id]:
        movie_list_name.append(movies.loc[newid].title) ### agrega el nombre de cada una de los id recomendados

movie_list_name

## Peliculas recomendadas
def MovieRecommender(movie_name = list(movies['title'].value_counts().index)):
    movie_list_name = []
    movie_id = movies[movies['title'] == movie_name].index
    movie_id = movie_id[0]
    for newid in idlist[movie_id]:
        movie_list_name.append(movies.loc[newid].title)
    return movie_list_name

print(interact(MovieRecommender))







