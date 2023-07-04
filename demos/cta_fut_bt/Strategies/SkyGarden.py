import pandas as pd
from wtpy import BaseCtaStrategy
from wtpy import CtaContext
import numpy as np
import math

class SkyGardenStra(BaseCtaStrategy):
    
    def __init__(self, name:str, code:str, barCnt:int,
                 period:str, margin_rate:float, money_pct:float, capital, cleartimes:list=[[1455, 1459]]):
        BaseCtaStrategy.__init__(self, name)

        self.__period__ = period
        self.__bar_cnt__ = barCnt
        self.__code__ = code
        self.__margin_rate__ = margin_rate # 保证金比率
        self.__money_pct__ = money_pct # 每次使用的资金比率
        self.__capital__ = capital
        self.today_entry = 0 # 限制每天开仓次数的参数
        self.__cleartimes__= cleartimes
    

    def on_init(self, context:CtaContext):
        code = self.__code__    #品种代码

        context.stra_get_bars(code, 'd1', self.__bar_cnt__, isMain=False)
        context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)
        context.stra_log_text("SkyGardenStra inited")
        pInfo = context.stra_get_comminfo(code)
        self.__volscale__ = pInfo.volscale


    def on_session_begin(self, context:CtaContext, curTDate:int):
        self.new_day = 1

        self.today_entry = 0

    def on_calculate(self, context:CtaContext):
        code = self.__code__    #品种代码

        trdUnit = 1

        theCode = code
        df_bars = context.stra_get_bars(code,'d1', self.__bar_cnt__, isMain=False)
        closes = df_bars.closes

        # 获取昨日收盘价
        last_day_close = closes[-1]
        df_bars = context.stra_get_bars(theCode, self.__period__, self.__bar_cnt__, isMain = True)
        # 尾盘清仓
        curPos = context.stra_get_position(code)
        curPrice = context.stra_get_price(code)
        curTime = context.stra_get_time()
        bCleared = False

        for tmPair in self.__cleartimes__:
            if curTime >= tmPair[0] and curTime <= tmPair[1]:
                if curPos != 0:  # 如果持仓不为0，则要检查尾盘清仓
                    context.stra_set_position(code, 0, "clear")  # 清仓直接设置仓位为0
                    context.stra_log_text("尾盘清仓")
                bCleared = True
                break

        if bCleared:
            return
        if self.new_day == 1:
            self.cur_open = df_bars.opens[-1]
            self.cur_high = df_bars.highs[-1]
            self.cur_low = df_bars.lows[-1]
            self.new_day = 0

        #把策略参数读进来，作为临时变量，方便引用
        margin_rate = self.__margin_rate__
        money_pct = self.__money_pct__
        volscale = self.__volscale__
        capital = self.__capital__
        trdUnit_price = volscale * margin_rate * curPrice
        cur_money = capital + context.stra_get_fund_data(0)
        curPos = context.stra_get_position(code)/trdUnit

        if curPos == 0 and self.today_entry == 0:
            if curPrice > self.cur_high and self.cur_open > last_day_close*1.01:
                context.stra_enter_long(code, math.floor(cur_money*money_pct/trdUnit_price),'enterlong')
                context.stra_log_text('当前价格：%.2f > 昨日收盘价：%.2f*1.01，做多%s手' % (curPrice, last_day_close, \
                                                                    math.floor(cur_money*money_pct/trdUnit_price)))
                self.today_entry = 1
                return
            if curPrice < self.cur_low and curPrice < last_day_close * 0.99:
                context.stra_enter_short(code, math.floor(cur_money*money_pct/trdUnit_price),'entershort')
                context.stra_log_text('当前价格:%.2f < 昨日收盘价：%.2f * 0.99，做空%s手' % (curPrice, self.cur_low, \
                                                                        math.floor(cur_money*money_pct/trdUnit_price)))
                self.today_entry = 1
                return