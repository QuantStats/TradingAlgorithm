import numpy as np
 
def initialize(context):
    
    # Check the pair trading rule daily
    schedule_function(check_pairs, date_rules.every_day(), time_rules.market_close(minutes=60))
    
    # Two airline stocks
    context.aal = sid(45971) #aal
    context.ual = sid(28051) #ual   
    
    # Flags if there is an opening position
    context.long = False
    context.short = False


def check_pairs(context, data):
    
    # Shorthand
    aal = context.aal
    ual = context.ual
    
    # Get pricing history
    prices = data.history([aal, ual], "price", 30, '1d')
    
    # Get the price dataframe
    short_prices = prices.iloc[-1:]
    
    # Get the longer 30 day mavg
    mavg_30 = np.mean(prices[aal] - prices[ual])
    
    # Get the std of the 30 day long window
    std_30 = np.std(prices[aal] - prices[ual])
    
    # Get the shorter span 1 day mavg
    mavg_1 = np.mean(short_prices[aal] - short_prices[ual])
    
    # Compute mavg z-score
    if std_30 > 0:
        zscore = (mavg_1 - mavg_30)/std_30
    
        # The two entry cases
        if zscore >0.95 and not context.short:
            # spread = - aal + ual
            order_target_percent(aal, -0.5) # short top
            order_target_percent(ual, 0.5) # long bottom
            context.short = True
            context.long = False
            
        elif zscore < -0.95 and not context.long:
            # spread = aal - ual
            order_target_percent(aal, 0.5) # long top
            order_target_percent(ual, -0.5) # short bottom
            context.short = False
            context.long = True
            
        # The exit case
        elif abs(zscore) < 0.05 and (context.long or\
                                   context.short):
            order_target_percent(aal, 0)
            order_target_percent(ual, 0)
            context.short = False
            context.long = False
        
        record('zscore', zscore)
