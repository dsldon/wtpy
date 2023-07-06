from wtpy import BaseCtaStrategy
from wtpy import CtaContext
import numpy as np
import math

class GridStra(BaseCtaStrategy):
    
    def __init__(self, name:str, code:str, barCnt:int, period:str, short_cnt:int, long_cnt:int, num:int, p1:float, p2:float, capital, margin_rate=0.1,stop_loss=0.8):
        BaseCtaStrategy.__init__(self, name)

        self.__short_cnt__ = short_cnt  # 计算短时均线时使用的天数
        self.__long_cnt__ = long_cnt  # 计算长时均线时使用的天数
        self.__num__ = num  # 单边网格格数
        self.__p1__ = p1    # 上涨时每格相比基准格的涨幅
        self.__p2__ = p2    # 下跌时每格相比基准格的跌幅(<0)
        self.__period__ = period    # 交易k线的时间级，如5分钟，1分钟
        self.__bar_cnt__ = barCnt   # 拉取的bar的次数
        self.__code__ = code        # 策略实例名称
        self.__capital__ = capital  # 起始资金
        self.__margin_rate__ = margin_rate  # 保证金率
        self.__stop_loss__ = stop_loss  # 止损系数，止损点算法为网格最低格的价格*stop_loss


    def on_init(self, context:CtaContext):
        code = self.__code__    # 品种代码

        context.stra_get_bars(code, 'm15', self.__bar_cnt__, isMain=False)  # 在策略初始化阶段调用一次后面要拉取的K线
        context.stra_get_bars(code, self.__period__, self.__bar_cnt__, isMain=True)
        context.stra_log_text("GridStra inited")

        pInfo = context.stra_get_comminfo(code)  # 调用接口读取品类相关数据
        self.__volscale__ = pInfo.volscale
        # 生成网格交易每格的边界以及每格的持仓比例
        self.__price_list__ = [1]
        self.__position_list__ = [0.5]
        num = self.__num__
        p1 = self.__p1__
        p2 = self.__p2__
        for i in range(num):
            self.__price_list__.append(1+(i+1)*p1)
            self.__price_list__.append(1+(i+1)*p2)
            self.__position_list__.append(0.5+(i+1)*0.5/num)
            self.__position_list__.append(0.5-(i+1)*0.5/num)
        self.__price_list__.sort()
        self.__position_list__.sort(reverse=True)

        print(self.__price_list__)
        print(self.__position_list__)


    def on_session_begin(self, context:CtaContext, curTDate:int):
        context.stra_log_text("{} trade begins".format(curTDate))
        return


    def on_bar(self, context:CtaContext, code:str, period:str, newBar:dict):
        # context.stra_log_text("{} code on bar called".format(code))
        return


    def on_calculate(self, context:CtaContext):
        code = self.__code__    #品种代码

        #把策略参数读进来，作为临时变量，方便引用
        margin_rate = self.__margin_rate__
        price_list = self.__price_list__
        position_list = self.__position_list__
        capital = self.__capital__
        volscale = self.__volscale__
        stop_loss = self.__stop_loss__
        short_cnt = self.__short_cnt__
        long_cnt = self.__long_cnt__
        theCode = code

        # 读取日线数据以计算均线的金叉
        df_bars = context.stra_get_bars(theCode, 'm15', self.__bar_cnt__, isMain=False)
        closes = df_bars.closes
        if len(closes) + 2 < long_cnt:
            context.stra_log_text("len(closes)={}".format(len(closes)))
            return

        ma_short_days1 = np.average(closes[-short_cnt:-1])
        ma_long_days1 = np.average(closes[-long_cnt:-1])
        ma_short_days2 = np.average(closes[-short_cnt - 1:-2])
        ma_long_days2 = np.average(closes[-long_cnt - 1:-2])
        # 读取最近self.__bar_cnt__条period分钟线
        context.stra_get_bars(theCode, self.__period__, self.__bar_cnt__, isMain=True)

        #读取当前仓位,价格
        curPos = context.stra_get_position(code)
        curPrice = context.stra_get_price(code)
        if curPos == 0:
            self.cur_money = context.stra_get_fund_data(0) + capital  # 当没有持仓时，用总盈亏加上初始资金计算出当前总资金

        trdUnit_price = volscale * curPrice * margin_rate  # 计算交易一手所选的期货所需的保证金

        if curPos == 0 and self.grid_pos == 0:
            if (ma_short_days1 > ma_long_days1) and (ma_long_days2 > ma_short_days2):
                self.benchmark_price = context.stra_get_price(code)
                self.grid_pos = 0.5
                context.stra_log_text("进场基准价格%.2f" % (self.benchmark_price))

        if self.grid_pos != 0 or (curPos != 0 and self.grid_pos == 0):
            for i in range(len(price_list)-1):
                if (price_list[i] <= (curPrice / self.benchmark_price)) and ((curPrice / self.benchmark_price) < price_list[i+1]):
                    if curPrice / self.benchmark_price < 1:
                        target_pos = position_list[i+1]
                    else:
                        target_pos = position_list[i]
            if curPrice / self.benchmark_price < price_list[0]:
                target_pos = 1
            elif curPrice / self.benchmark_price > price_list[-1]:
                target_pos = 0
            # 止损逻辑 1
            if (curPrice / self.benchmark_price) > (price_list[-1] * (2-stop_loss)):
                target_pos = 0
                context.stra_exit_short(code, abs(context.stra_get_position(code)), 'exitshort')
                context.stra_log_text("价格超出最大上边界*%s，全部平空" % (2-stop_loss))
                self.grid_pos = target_pos
                return
            # 止损逻辑 2
            if (curPrice / self.benchmark_price) < (price_list[0] * stop_loss):
                target_pos = 0
                context.stra_exit_long(code, context.stra_get_position(code), 'exitlong')
                context.stra_log_text("价格低于最大下边界*%s，止损，全部平多" % (stop_loss))
                self.grid_pos = target_pos
                return
            if (target_pos > self.grid_pos) and (curPos >= 0):
                context.stra_enter_long(code, math.floor((target_pos-self.grid_pos)*self.cur_money/trdUnit_price), 'enterlong')
                context.stra_log_text("做多%d手,目标仓位%.2f,当前仓位%.2f,当前手数%d" % (math.floor((target_pos-self.grid_pos)*self.cur_money/trdUnit_price), target_pos, self.grid_pos,\
                                                                      context.stra_get_position(code)))
                self.grid_pos = target_pos
                return
            elif (target_pos < self.grid_pos) and (curPos <= 0):
                context.stra_enter_short(code, math.floor((self.grid_pos-target_pos)*self.cur_money/trdUnit_price), 'entershort')
                context.stra_log_text("做空%d手,目标仓位%.2f,当前仓位%.2f,当前手数%d" % (math.floor((self.grid_pos-target_pos)*self.cur_money/trdUnit_price), target_pos, self.grid_pos,\
                                                                      context.stra_get_position(code)))
                self.grid_pos = target_pos
                return
            elif (target_pos < self.grid_pos) and (curPos >= 0):
                context.stra_exit_long(code, math.floor((self.grid_pos-target_pos)*self.cur_money/trdUnit_price), 'exitlong')
                context.stra_log_text("平多%d手,目标仓位%.2f,当前仓位%.2f,当前手数%d" % (math.floor((self.grid_pos-target_pos)*self.cur_money/trdUnit_price), target_pos, self.grid_pos,\
                                                                      context.stra_get_position(code)))
                self.grid_pos = target_pos
                return
            elif (target_pos > self.grid_pos) and (curPos <= 0):
                context.stra_exit_short(code, math.floor((target_pos - self.grid_pos) * self.cur_money / trdUnit_price),
                                        'exitshort')
                context.stra_log_text("平空%d手,目标仓位%.2f,当前仓位%.2f,当前手数%d" % (
                math.floor((target_pos - self.grid_pos) * self.cur_money / trdUnit_price), target_pos, self.grid_pos, \
                context.stra_get_position(code)))
                self.grid_pos = target_pos
                return