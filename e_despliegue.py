import numpy as np
import pandas as pd
import sqlite3 as sql
import a_funciones as fn ## para procesamiento
import openpyxl


####Paquete para sistema basado en contenido ####
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors


def preprocesar():

    #### conectar_base_de_Datos#################
    conn=sql.connect('data\\db_movies')
    cur=conn.cursor()

    ######## convertir datos crudos a bases filtradas por usuarios que tengan cierto número de calificaciones
    fn.ejecutar_sql('preprocesamiento.sql', cur)

    ##### llevar datos que cambian constantemente a python ######
    movies=pd.read_sql('select * from movies2', conn )
    ratings=pd.read_sql('select * from ratings2', conn)
    usuarios=pd.read_sql('select distinct (user_id) as user_id from ratings_final2',conn)

    
    #### transformación de datos crudos - Preprocesamiento ################
    movies['año_estreno']=movies.año_estreno.astype('int')

    ##### escalar para que año esté en el mismo rango ###
    sc=MinMaxScaler()
    movies[["año_estrenosc"]]=sc.fit_transform(movies[['año_estreno']])

    ## eliminar filas que no se van a utilizar ###
    movies_dum1=movies.drop(columns=['movieId','title','conteo','año_estreno'])

    return movies_dum1,movies, conn, cur

##########################################################################
###############Función para entrenar modelo por cada usuario ##########
###############Basado en contenido todo lo visto por el usuario Knn#############################
def recomendar(user_id):
    
    movies_dum1, movies, conn, cur= preprocesar()
    
    ratings=pd.read_sql('select *from ratings_final where user_id=:user',conn, params={'user':user_id})
    l_movies=ratings['movieId'].to_numpy()
    movies_dum1[['movieId','title']]=movies[['movieId','title']]
    movies_nr=boo_dum2[books_dum2['isbn'].isin(l_books_r)]
    books_r=books_r.drop(columns=['isbn','book_title'])
    books_r["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    centroide=books_r.groupby("indice").mean()
    
    
    books_nr=books_dum2[~books_dum2['isbn'].isin(l_books_r)]
    books_nr=books_nr.drop(columns=['isbn','book_title'])
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(books_nr)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0]
    recomend_b=books.loc[ids][['book_title','isbn']]
    
    
    return recomend_b


##### Generar recomendaciones para usuario lista de usuarios ####
##### No se hace para todos porque es muy pesado #############
def main(list_user):
    
    recomendaciones_todos=pd.DataFrame()
    for user_id in list_user:
            
        recomendaciones=recomendar(user_id)
        recomendaciones["user_id"]=user_id
        recomendaciones.reset_index(inplace=True,drop=True)
        
        recomendaciones_todos=pd.concat([recomendaciones_todos, recomendaciones])

    recomendaciones_todos.to_excel('C:\\cod\\LEA3_RecSys\\salidas\\reco\\recomendaciones.xlsx')
    recomendaciones_todos.to_csv('C:\\cod\\LEA3_RecSys\\salidas\\reco\\recomendaciones.csv')


if __name__=="__main__":
    list_user=[52853,31226,167471,8066 ]
    main(list_user)
    

import sys
sys.executable