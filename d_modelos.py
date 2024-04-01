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
final = pd.read_sql('select * from ratings_final2', conn)

######################################################################
################## 1. sistemas basados en popularidad ###############
#####################################################################


##### recomendaciones basado en popularidad ######

#### mejores calificadas que tengan calificacion
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








