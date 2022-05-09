truncate table public.s3_data_loader_util_config;
truncate table s3_data_loader_util;
truncate table s3_data_loader_log;

truncate table customer_tbl;
truncate table customer_tbl1;
truncate table customer_tbl2;
truncate table customer_tbl3;
truncate table customer_tbl4;
truncate table customer_tbl5;
truncate table customer_tbl6;


select 'customer_tbl' ,count(*) from  customer_tbl union 
select 'customer_tbl1' ,count(*) from  customer_tbl1 union 
select 'customer_tbl2' ,count(*) from  customer_tbl2 union 
select 'customer_tbl3' ,count(*) from  customer_tbl3 union 
select 'customer_tbl4' ,count(*) from  customer_tbl4 union
select 'customer_tbl5' ,count(*) from  customer_tbl5 union 
select 'customer_tbl6' ,count(*) from  customer_tbl6 
union
select 'rs_customer_fact' ,count(*) from  rs_customer_fact;



