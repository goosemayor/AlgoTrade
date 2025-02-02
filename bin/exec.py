
import os, sys, time
sys.path.append('/your_path/AlgoLearn/')

from algosim.engine import queue, timeindex
from algosim.tick_handler import online_handler, offline_handler
from algosim.feature_handler import online_feature_handler, offline_feature_handler
from algosim.model_handler import online_model_handler, offline_model_handler
from algosim.position_handler import position_handler
from algosim.algo_handler import online_algo_handler_cxh
from algosim.order_handler import order_handler
from algosim.execution_handler import sim_exec_handler


# Queue========================================================================
eq = queue.EventQueue()
timeObj = timeindex.TimeIndex(eq, date=self.date, store_path=self.store_path)    

# TickHandler========================================================================
tickObj = online_handler.OnlineTickHandler(csv_dir=data_path, 
                                        date=self.date, 
                                        events_queue=eq,
                                        store_path=self.store_path, 
                                        subscribe_tickers=subscribe_tickers, 
                                        subscribe_fields=subscribe_fields)

# tickObj = offline_handler.OfflineTickHandler(off_path=self.store_path, date=self.date, events_queue=eq,
#                             subscribe_tickers=subscribe_tickers, subscribe_fields=subscribe_fields)


# FeatureHandler========================================================================

featureObj = online_feature_handler.OnlineFeatureHandler(eq, 
                                                         feature_name_list=['f1', 'f3'],
                                                         subscribe_fields=subscribe_fields,
                                                        store_path=self.store_path)
    
#         featureObj = offline_feature_handler.OfflineFeatureHandler(eq,
                                                        # subscribe_fields=subscribe_fields,
#                                                                  off_path=self.store_path)

#ModelHandler========================================================================
modelObj = online_model_handler.OnlineModelHandler(eq, 
                                                store_path=self.store_path)
#         modelObj = offline_model_handler.OfflineModelHandler(eq, off_path=self.store_path)


#PositionHandler========================================================================

posObj = position_handler.PositionHandler(tick_handler=tickObj, init_position=init_position,
                          init_cash=init_cash, store_path=self.store_path)


# ========================================================================

algoObj = online_algo_handler_cxh.OnlineAlgoHandler(eq, 
                                                posObj, 
                                                tick_handler=tickObj, 
                                                store_path=self.store_path)



# ========================================================================

orderObj = order_handler.OrderHandler(eq, tick_handler=tickObj, 
                                                position_handler=posObj,
                                                limit_position=init_position,
                                                store_path=self.store_path)

# ========================================================================

execObj = sim_exec_handler.SimExecHandler(eq,
                                         tickObj,
                                        store_path=self.store_path)




# ========================================================================
eq.register('TIME', tickObj)
eq.register('TICK', featureObj)
eq.register('FEATURE', modelObj)
eq.register('MODEL', algoObj)
eq.register('ALGO', orderObj)
eq.register('ORDER', execObj)
eq.register('FILL', posObj)

# ========================================================================
for i in timeObj.get_all_timestamp():
    timeObj.update_timeindex()
    eq.run()

timeObj.store()
tickObj.store()
featureObj.store()
modelObj.store()
algoObj.store()
posObj.store()
orderObj.store()
execObj.store()



# ========================================================================
eq.unregister('TIME', tickObj)
eq.unregister('TIME', featureObj)
eq.unregister('FEATURE', modelObj)
eq.unregister('MODEL', algoObj)
eq.unregister('ALGO', orderObj)
eq.unregister('ORDER', execObj)
eq.unregister('FILL', posObj)



# ========================================================================
from algosim.statistics import trades
b = trades.Trades(account_path=self.store_path)
b.run()

# ========================================================================
from algosim.statistics import profiling
pro = profiling.Profiling(account_path=self.store_path, benchmark='benchmark')
pro.run()
