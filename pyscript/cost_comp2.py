'''
test=# set search_path to tpch10g;

test=# select max(l_extendedprice) from lineitem;
max    
-----------
104949.50
(1 row)

test=# select max(l_quantity) from lineitem;
max  
-------
50.00
(1 row)

explain
select
  sum(case
      when o_orderpriority = '1-URGENT'
          OR o_orderpriority = '2-HIGH'
          then 1
      else 0
  end) as high_line_count,
  sum(case
      when o_orderpriority <> '1-URGENT'
          AND o_orderpriority <> '2-HIGH'
          then 1
      else 0
  end) AS low_line_count
from
  lineitem inner join orders on l_orderkey = o_orderkey
where
  l_extendedprice between $1 and $1+20000
  and
  l_quantity <= $2;

'''
import psycopg2
import time
import random

conn = psycopg2.connect("dbname=test user=postgres")
cur = conn.cursor()
cur.execute('set search_path to tpch10g')
cur.execute("set work_mem to '2GB'")

price_lows = list(range(0, 101000, 10000))
quantity_highs = list(range(5, 51, 5))

#num = 10

def get_counts():
    for price in price_lows:
        for quantity in quantity_highs:
            sql = f'''
            select count(*)
            from lineitem
            where l_extendedprice between {price} and {price+2000} 
              and l_quantity <= {quantity}'''

            cur.execute(sql)
            c = cur.fetchone()[0]
            print('price_low: %d, quantity_high: %d, count: %d' % (price, quantity, c), flush=True)


def run_all_queries():
    for price in price_lows:
        for quantity in quantity_highs:

            sql = f'''
                select
                  l_shipmode,
                  sum(case
                      when o_orderpriority = '1-URGENT'
                          OR o_orderpriority = '2-HIGH'
                          then 1
                      else 0
                  end) as high_line_count,
                  sum(case
                      when o_orderpriority <> '1-URGENT'
                          AND o_orderpriority <> '2-HIGH'
                          then 1
                      else 0
                  end) AS low_line_count
                from
                  lineitem inner join orders on l_orderkey = o_orderkey
                where l_extendedprice between {price} and {price+2000} 
                  and l_quantity <= {quantity}
                group by
                  l_shipmode'''

            start_time = time.time()
            cur.execute(sql)
            cur.fetchall()
            elapsed_time = time.time() - start_time
            print('price_low: %d, quantity_high: %d, elapsed_time: %.6f' % (price, quantity, elapsed_time), flush=True)

def turn_on_seq_only():
    print('seq')
    cur.execute('set enable_seqscan to on')
    cur.execute('set enable_indexscan to off')
    cur.execute('set enable_bitmapscan to off')

def turn_on_index_scan_only():
    print('index scan')
    cur.execute('set enable_seqscan to off')
    cur.execute('set enable_indexscan to on')
    cur.execute('set enable_bitmapscan to on')

#get_counts()
#run_all_queries()

print('merge join only')
cur.execute('set enable_hashjoin to off')
cur.execute('set enable_mergejoin to on')
cur.execute('set enable_nestloop to off')

turn_on_seq_only()
run_all_queries()
run_all_queries()
print()

turn_on_index_scan_only()
run_all_queries()
run_all_queries()
print()

# hash join only
print('hash join only')
cur.execute('set enable_hashjoin to on')
cur.execute('set enable_mergejoin to off')
cur.execute('set enable_nestloop to off')

turn_on_seq_only()
run_all_queries()
run_all_queries()
print()

turn_on_index_scan_only()
run_all_queries()
run_all_queries()
print()

# nested loop join only
print('nested loop join only')
cur.execute('set enable_hashjoin to off')
cur.execute('set enable_mergejoin to off')
cur.execute('set enable_nestloop to on')

turn_on_index_scan_only()
run_all_queries()
run_all_queries()
print()


cur.close()
conn.close()

