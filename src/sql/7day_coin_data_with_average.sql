

/*
7 day market volume average for new coins.
This is used as a source table for another query - 

Includes:
- Date of the 1st Day
- Date of the 7th Day
- 7 day volume average 
- Coin symbol

puts this into a new table called '7day_coins_wdate'
*/ 


with simpletable as (

select 


ucdcc."Date",
ucdcc.symbol,
--avg(ucdcc.volume) as volume_avg_day_7,
ucdcc.volume,
--ucdcc.price

first_value (ucdcc."price") 
OVER(
  PARTITION BY ucdcc."symbol"
        ORDER BY ucdcc."Date" desc
       RANGE BETWEEN 
           UNBOUNDED PRECEDING AND 
            UNBOUNDED FOLLOWING
   )  price_at_day7,

first_value (ucdcc."Date") 
OVER(
  PARTITION BY ucdcc."symbol"
        ORDER BY ucdcc."Date" desc
       RANGE BETWEEN 
           UNBOUNDED PRECEDING AND 
            UNBOUNDED FOLLOWING
   )  date_at_day7

from public.updated_crypto_data_coingecko_csv ucdcc 

inner join (

select 

symbol,
first_value ("Date") 
    OVER(
    PARTITION BY "symbol"
        ORDER BY "Date"
        RANGE BETWEEN 
            UNBOUNDED PRECEDING AND 
            UNBOUNDED FOLLOWING
    )  first_day,
first_value ("Date") 
    OVER(
    PARTITION BY "symbol"
        ORDER BY "Date"
        RANGE BETWEEN 
            UNBOUNDED PRECEDING AND 
            UNBOUNDED FOLLOWING
    ) + interval '7 day' last_day

from public.updated_crypto_data_coingecko_csv ucdcc2  

    
  ) windows on windows.symbol = ucdcc.symbol and ucdcc."Date" >= windows.first_day::TIMESTAMP and ucdcc."Date" <= windows.last_day::TIMESTAMP
    
-- group by ucdcc.symbol, ucdcc.volume, ucdcc.price, ucdcc."Date"
  
)

select 

symbol,
avg(volume) as average_volume,
price_at_day7,
date_at_day7

INTO public."7day_coins_wdate"
from simpletable
group by symbol, price_at_day7, date_at_day7

;
