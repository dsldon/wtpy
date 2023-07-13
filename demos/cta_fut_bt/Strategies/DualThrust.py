from wtpy import BaseCtaStrategy
from wtpy import CtaContext
import numpy as np

class StraDualThrust(BaseCtaStrategy):
    
    def __init__(self, name:str, code:str, barCnt:int, period:str, k1:float, k2:float, slTicks = 0, spTicks = 0):
        BaseCtaStrategy.__init__(self, name)

        self.__k1__ = k1
        self.__k2__ = k2

        self.__period__ = period
        self.__bar_cnt__ = barCnt + 1
        self.__code__ = code

        self.__stop_loss__ = slTicks
        self.__stop_prof__ = spTicks

    def on_init(self, context:CtaContext):
        code = self.__code__    #品种代码

        #这里演示了品种信息获取的接口
        #pInfo = context.stra_get_comminfo(code)
        #print(pInfo)

        context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)
        context.stra_log_text("DualThrust inited")

    
    def on_calculate(self, context:CtaContext):
        code = self.__code__    #品种代码
        # 成交手数
        trdUnit = 1
    
        #读取当前仓位
        curPos = context.stra_get_position(code)/trdUnit
        #读取最近50条1分钟线(dataframe对象)
        df_bars = context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain = True)

        #把策略参数读进来，作为临时变量，方便引用
        bar_cnt = self.__bar_cnt__
        k1 = self.__k1__
        k2 = self.__k2__

        #平仓价序列、最高价序列、最低价序列
        closes = df_bars.closes
        highs = df_bars.highs
        lows = df_bars.lows

        curPx = closes[-1]

        needCut = False
        cutTag = ""
        if curPos != 0:
            opentag = "enterlong" if curPos>0 else "entershort"
            openpx = context.stra_get_detail_cost(code, opentag)
            diffPx = (curPx - openpx)*curPos/abs(curPos)
            if self.__stop_loss__ != 0:
                if diffPx <= self.__stop_loss__:
                    needCut = True
                    cutTag = "cutloss"
            if self.__stop_prof__ != 0:
                if diffPx >= self.__stop_prof__:
                    needCut = True
                    cutTag = "cutwin"

        if needCut:
            if curPos > 0:
                context.stra_exit_long(code, abs(curPos)*trdUnit, cutTag)
            else:
                context.stra_exit_short(code, abs(curPos)*trdUnit, cutTag)
            return

        #读取days天之前到上一个交易日位置的数据
        hh = np.amax(highs[-bar_cnt:-1])
        hc = np.amax(closes[-bar_cnt:-1])
        ll = np.amin(lows[-bar_cnt:-1])
        lc = np.amin(closes[-bar_cnt:-1])

        #读取今天的开盘价、最高价和最低价
        # lastBar = df_bars.get_last_bar()
        openpx = df_bars.opens[-1]
        highpx = df_bars.highs[-1]
        lowpx = df_bars.lows[-1]

        '''
        !!!!!这里是重点
        1、首先根据最后一条K线的时间，计算当前的日期
        2、根据当前的日期，对日线进行切片,并截取所需条数
        3、最后在最终切片内计算所需数据
        '''

        #确定上轨和下轨
        upper_bound = openpx + k1* max(hh-lc,hc-ll)
        lower_bound = openpx - k2* max(hh-lc,hc-ll)

        if curPos == 0:
            if highpx >= upper_bound:
                context.stra_enter_long(code, 1*trdUnit, 'enterlong')
                context.stra_log_text("向上突破%.2f>=%.2f，多仓进场" % (highpx, upper_bound))
                return

            if lowpx <= lower_bound:
                context.stra_enter_short(code, 1*trdUnit, 'entershort')
                context.stra_log_text("向下突破%.2f<=%.2f，空仓进场" % (lowpx, lower_bound))
                return
        elif curPos > 0:
            if lowpx <= lower_bound:
                context.stra_exit_long(code, 1*trdUnit, 'exitlong')
                context.stra_log_text("向下突破%.2f<=%.2f，多仓出场" % (lowpx, lower_bound))
                return
        else:
            if highpx >= upper_bound:
                context.stra_exit_short(code, 1*trdUnit, 'exitshort')
                context.stra_log_text("向上突破%.2f>=%.2f，空仓出场" % (highpx, upper_bound))
                return


    def on_tick(self, context:CtaContext, stdCode:str, newTick:dict):
        #context.stra_log_text ("on tick fired")
        return