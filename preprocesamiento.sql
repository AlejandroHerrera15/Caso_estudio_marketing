
---tabla con las películas que han sido vistas por más de 10 usuarios
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



drop table if exists  ratings_f;

create table  ratings_f as
select a.UserId as user_id,
a.movieId as movieId,
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







