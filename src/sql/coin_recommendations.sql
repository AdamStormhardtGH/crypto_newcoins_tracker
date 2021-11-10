/* 

Provide an overview for all coins, with key metrics:
- first day added in db
- latest day we have data for
- average volume across the data we have
- latest volume
- TODO: week this coin belongs to once it's got 7 days or more of data
- TODO: threshold met of 100m?

*/

-- View Example
CREATE OR REPLACE VIEW coin_recommendations AS  --create table 
SELECT distinct  

id, 
symbol,
"name",
added_date,
latest_price,
latest_total_volumes,
average_total_volumes,
latest_date


-- added_date + interval '24' hour as day_plus1,
-- now() as now



FROM "coin_analysis"."watchlist"
inner join (
  select 
  id as wlid,
  last_value(prices)
    over(partition by id
    order by "date" 
    rows between unbounded preceding and unbounded following) as latest_price,
  last_value(total_volumes)
    over(partition by id
    order by "date" 
    rows between unbounded preceding and unbounded following) as latest_total_volumes,
  last_value("date")
    over(partition by id
    order by "date" 
    rows between unbounded preceding and unbounded following) as latest_date,
  date_add('day',6, to_date(to_char(
    date_add('day', 6, first_value("date")
    over(partition by id
    order by "date" asc
    --rows between unbounded preceding and unbounded following)::timestamp + interval '6 day'), 'IYYY-IW'),'iyyy-iw') + interval '6day'  -- postgres code
    rows between unbounded preceding and unbounded following) ), 'IYYY-IW'),'iyyy-iw') )

   as end_of_week_buy_date
  
 
  
  from "coin_analysis"."watched-coin-data" 
  
  
  ) latest_report on latest_report.wlid = "coin_analysis"."watchlist".id
  
  left join (
    
    select 
    id as avg_id, 
    avg(total_volumes) as average_total_volumes
    from "coin_analysis"."watched-coin-data" 
    group by id
    ) average_report on average_report.avg_id = "coin_analysis"."watchlist".id
  

where (added_date + interval '24' hour)< now()
and latest_total_volumes > 1300000
and latest_price < 0.003
