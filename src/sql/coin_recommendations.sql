-- View Example
CREATE OR REPLACE VIEW coin_recommendations AS
SELECT distinct  

id, 
symbol,
name,
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
  first_value(prices)
    over(partition by id
    order by "date" desc
    rows between unbounded preceding and unbounded following) as latest_price,
  first_value(total_volumes)
    over(partition by id
    order by "date" desc
    rows between unbounded preceding and unbounded following) as latest_total_volumes,
  first_value("date")
    over(partition by id
    order by "date" desc
    rows between unbounded preceding and unbounded following) as latest_date
  
 
  
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
