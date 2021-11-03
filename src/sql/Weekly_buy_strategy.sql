

/*
Weekly Buy strategy: 
- Once a coin has 7 days of volume available, we put it into consideration for a purchase at the end of the week(eg. Saturday)
- We select coin with the highest volume coin for that week
- We buy that coin
*/


with report as (
    with calc_weekbuy as(
        with base_table as (
        select *,
        extract(week from cast(date_at_day7 as date)) as week_num,
        extract(year from cast(date_at_day7 as date)) as year_num,
        to_date(to_char(date_at_day7, 'IYYY-IW'),'iyyy-iw') + interval '6 day' as year_week

        from "7day_coins_wdate" dcw 
        where date_at_day7 > CAST('2020-01-01' as date)
        )

    select 
    distinct

    (FIRST_VALUE ( symbol ) OVER ( partition by year_week ORDER BY price_at_day7 desc ) ) as  week_winner,
    year_week

    from base_table 
    order by year_week  asc  
    )

select 
distinct
* 

from 
calc_weekbuy

inner join (

select 
symbol,
"Date",
price,
(FIRST_VALUE ( "price" ) OVER ( partition by "symbol" ORDER BY "Date" desc ) ) as  latest_price,
(FIRST_VALUE ( "price" ) OVER ( partition by "symbol" ORDER BY "Date" desc ) - price) / price +1 as  price_change_perc

from public.updated_crypto_data_coingecko_csv ucdcc 
where price >0
) j on j.symbol =  calc_weekbuy.week_winner and j."Date" = calc_weekbuy.year_week

order by "Date" asc)  -- 100185.74394816707%


select sum(price_change_perc) as gainz,
 count(1) as count_of_payments,
 420*count(1) as "cost",
 sum(price_change_perc)*120 as "money_gains"


from report
;