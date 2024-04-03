
---tabla con las películas que han sido calificadas por más de 10 usuarios
drop table if exists movies_vistas;

create table movies_vistas as select movieId,
                         count(*) as conteo
                         from ratings
                         group by movieId
                         having conteo >10
                         order by conteo desc ;

drop table if exists movies1;
create table movies1 as select movieId, title, genres
                        from movies;

-----------------------------------------------------------------

drop table if exists  ratings_f;

create table  ratings_f as
select a.UserId as user_id,
a.movieId as movie_id,
a.rating as movie_rating,
a.timestamp as timestamp
from ratings a 
inner join movies_vistas b
on a.movieId =b.movieId;


drop table if exists movies_f;

create table movies_f as select 
a.*,
b.*
from movies1 a inner join
movies_vistas b on a.movieId = b.movieId;

-----------------------------------------------------------------
-- Tabla final 

DROP TABLE IF EXISTS ratings_final;

CREATE TABLE ratings_final AS
SELECT 
    a.user_id,
    a.movie_id,
    a.movie_rating,
    a.timestamp,
    b.*
FROM 
    ratings_f a
INNER JOIN 
    movies_f b ON a.movie_id = b.movieId;





